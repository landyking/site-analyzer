import logging
import os
import tarfile
import shutil
from typing import Iterable
import boto3
from botocore.exceptions import ClientError
from .config import settings

logger = logging.getLogger(__name__)

# Connect to MinIO
s3 = boto3.client(
    "s3",
    endpoint_url= settings.STORAGE_ENDPOINT if settings.STORAGE_ENDPOINT != "#" else None,
    aws_access_key_id=settings.STORAGE_ACCESS_KEY,
    aws_secret_access_key=settings.STORAGE_SECRET_KEY,
    region_name=settings.STORAGE_REGION
)

bucket_name = settings.STORAGE_BUCKET

bucket_inputs_dir = "inputs"
bucket_outputs_dir = "outputs"

logger.info("Connected to storage service at %s", settings.STORAGE_ENDPOINT)

def get_bucket_meta_info() -> dict:
    try:
        response = s3.head_bucket(Bucket=bucket_name)
        return {
            "Name": bucket_name,
            "CreationDate": response["ResponseMetadata"]["HTTPHeaders"]["date"],
            "Owner": response["ResponseMetadata"]["HTTPHeaders"]["x-amz-request-id"]
        }
    except ClientError as e:
        logger.error("Error fetching bucket meta-info: %s", e)
        return {}

# define a function to logging basic meta-info of the bucket into console
def log_bucket_meta_info() -> None:
    meta_info = get_bucket_meta_info()
    logger.info("Bucket Name: %s", meta_info.get("Name", "Unknown"))
    logger.info("Creation Date: %s", meta_info.get("CreationDate", "Unknown"))
    logger.info("Owner: %s", meta_info.get("Owner", "Unknown"))


def save_file(src_path: str, dest_path: str) -> None:
    try:
        s3.upload_file(src_path, bucket_name, dest_path)
    except ClientError as e:
        logger.error("Error uploading file: %s", e)
        # raise new internal error
        raise RuntimeError("Error uploading file")

def save_task_file(src_path: str, user_id: int, task_id: int) -> str:
    file_name = os.path.basename(src_path)
    dest_path = f"{bucket_outputs_dir}/{user_id}/{task_id}/{file_name}"
    save_file(src_path, dest_path)
    return dest_path


def delete_file(key: str) -> bool:
    """Delete a single object from storage.

    Typical key format for task output: "<user_id>/<task_id>/<filename>" as produced by save_task_file.
    Returns True if deletion succeeds (or object absent), False otherwise.
    Never raises to keep upstream logic resilient.
    """
    try:
        s3.delete_object(Bucket=bucket_name, Key=key)
        return True
    except ClientError as e:
        # Ignore not found; log others
        err_code = getattr(e, "response", {}).get("Error", {}).get("Code")
        if err_code not in ("NoSuchKey",):
            logger.warning("delete_file failed for key %s: %s", key, e)
        return False


def delete_files(keys: Iterable[str]) -> dict:
    """Batch delete objects (best effort) for the provided iterable of keys.

    The CRUD layer calls this when deleting a map task to ensure all previously
    uploaded result artifacts are removed from object storage.

    Returns a summary dict: {requested, deleted, errors}.
    """
    keys_list = [k for k in keys if k]
    if not keys_list:
        return {"requested": 0, "deleted": 0, "errors": 0}
    deleted = 0
    errors = 0
    # S3 DeleteObjects allows up to 1000 per request
    for i in range(0, len(keys_list), 1000):
        chunk = keys_list[i:i+1000]
        try:
            resp = s3.delete_objects(
                Bucket=bucket_name,
                Delete={"Objects": [{"Key": k} for k in chunk], "Quiet": True},
            )
            deleted += len(resp.get("Deleted", []))
            errors += len(resp.get("Errors", []))
            if resp.get("Errors"):
                logger.warning("Some keys failed to delete: %s", [e.get('Key') for e in resp["Errors"]])
        except ClientError as e:
            errors += len(chunk)
            logger.warning("delete_files chunk failed (%s): %s", len(chunk), e)
    return {"requested": len(keys_list), "deleted": deleted, "errors": errors}

def generate_presigned_url(key: str, expires_in_seconds: int = settings.STORAGE_SIGN_EXPIRE_SECONDS) -> str:
    # Generate a presigned URL for download
    url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket_name, "Key": key},
        ExpiresIn=expires_in_seconds
    )
    return url


# ------------------------------
# Initialization helpers
# ------------------------------

def _list_tgz_keys_under_prefix(prefix: str) -> list:
    """List all keys ending with .tgz under the given prefix in the configured bucket.

    Notes:
    - This function assumes `prefix` is an object key prefix within the configured bucket,
      not a full s3:// URL.
    - It paginates results to cover more than 1000 objects.
    """
    paginator = s3.get_paginator("list_objects_v2")
    tgz_keys: list[str] = []
    try:
        for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix.rstrip("/") + "/"):
            for obj in page.get("Contents", []):
                key = obj.get("Key", "")
                if key.endswith(".tgz"):
                    tgz_keys.append(key)
    except ClientError as e:
        logger.error("Failed to list objects under prefix '%s': %s", prefix, e)
    return tgz_keys


def download_tgz_archives(bucket_dir: str, local_cache_dir: str | None = None) -> list:
    """Download all .tgz files under `bucket_dir` to a local cache directory.

    - If `local_cache_dir` is None, defaults to `~/.site-analyzer`.
    - Existing same-named local files will be deleted before download.

    Returns a list of absolute local file paths for the downloaded archives.
    """
    cache_dir = os.path.abspath(os.path.expanduser(local_cache_dir or os.path.join("~", ".site-analyzer")))
    os.makedirs(cache_dir, exist_ok=True)

    keys = _list_tgz_keys_under_prefix(bucket_dir)
    local_files: list[str] = []
    for key in keys:
        filename = os.path.basename(key)
        local_path = os.path.join(cache_dir, filename)
        # Remove existing file if present
        try:
            if os.path.exists(local_path):
                os.remove(local_path)
        except OSError as e:
            logger.warning("Failed to remove existing file '%s': %s", local_path, e)
        # Download
        try:
            s3.download_file(bucket_name, key, local_path)
            local_files.append(local_path)
            logger.info("Downloaded %s -> %s", key, local_path)
        except ClientError as e:
            logger.error("Failed to download '%s': %s", key, e)
    return local_files


def _safe_extract_tgz(archive_path: str, dest_dir: str) -> list:
    """Safely extract a .tgz archive into `dest_dir` with overwrite behavior.

    Security considerations:
    - Prevent path traversal (no extraction outside of `dest_dir`).
    - Skip symlinks and hardlinks to avoid unexpected link targets.

    Overwrite behavior:
    - If a target path already exists as a file or symlink, it will be removed before writing.
    - Directories are created with exist_ok=True; if a directory exists where a file will be
      written, the directory is removed first.

    Returns a list of extracted member relative paths.
    """
    extracted: list[str] = []
    dest_dir_abs = os.path.abspath(dest_dir)
    os.makedirs(dest_dir_abs, exist_ok=True)
    with tarfile.open(archive_path, mode="r:gz") as tf:
        for member in tf.getmembers():
            name = member.name
            if not name or name.startswith("/"):
                # Normalize absolute/empty names
                name = name.lstrip("/")
            # Normalize and guard against path traversal
            target_path = os.path.abspath(os.path.join(dest_dir_abs, name))
            if not target_path.startswith(dest_dir_abs + os.sep) and target_path != dest_dir_abs:
                logger.warning("Skipping suspicious path in archive '%s': %s", archive_path, name)
                continue

            if member.issym() or member.islnk():
                logger.warning("Skipping link member in archive '%s': %s", archive_path, name)
                continue

            if member.isdir():
                try:
                    os.makedirs(target_path, exist_ok=True)
                    extracted.append(os.path.relpath(target_path, dest_dir_abs))
                except OSError as e:
                    logger.warning("Failed to create directory '%s': %s", target_path, e)
                continue

            # For regular files and others: ensure parent exists, remove conflicting path
            parent = os.path.dirname(target_path)
            os.makedirs(parent, exist_ok=True)
            if os.path.isdir(target_path):
                try:
                    shutil.rmtree(target_path)
                except OSError as e:
                    logger.warning("Failed to remove existing directory '%s': %s", target_path, e)
            elif os.path.exists(target_path):
                try:
                    os.remove(target_path)
                except OSError as e:
                    logger.warning("Failed to remove existing file '%s': %s", target_path, e)

            # Extract file content
            try:
                f = tf.extractfile(member)
                if f is None:
                    # Could be a special member; skip
                    continue
                with f as src, open(target_path, "wb") as out:
                    shutil.copyfileobj(src, out)
                # Apply basic permissions if available
                try:
                    os.chmod(target_path, member.mode)
                except Exception:
                    pass
                extracted.append(os.path.relpath(target_path, dest_dir_abs))
            except Exception as e:
                logger.warning("Failed to extract '%s' from '%s': %s", name, archive_path, e)
    return extracted


def extract_archives_to_input_dir(local_archives: Iterable[str], input_dir: str) -> dict:
    """Extract a list of .tgz archives into `input_dir` with overwrite.

    Returns a summary dict: {archives, extracted_files}.
    """
    input_dir_abs = os.path.abspath(os.path.expanduser(input_dir))
    os.makedirs(input_dir_abs, exist_ok=True)
    all_extracted: list[str] = []
    archives_list = list(local_archives)
    for archive in archives_list:
        try:
            extracted = _safe_extract_tgz(archive, input_dir_abs)
            all_extracted.extend(extracted)
            logger.info("Extracted %s into %s (%d entries)", archive, input_dir_abs, len(extracted))
        except (tarfile.TarError, OSError) as e:
            logger.error("Failed to extract archive '%s': %s", archive, e)
    return {"archives": len(archives_list), "extracted_files": len(all_extracted)}


def initialize_input_dir_from_bucket() -> dict:
    """Initialize a local input directory from .tgz archives stored under a bucket prefix.

    Steps:
    1) Download all `.tgz` objects under `bucket_dir` into `~/.site-analyzer` (removing duplicates first).
    2) Extract each archive into `input_dir`, overwriting existing files if necessary.

    Assumptions:
    - `bucket_dir` is a prefix within the configured bucket (`settings.STORAGE_BUCKET`).

    Returns a summary dict: {downloaded, extracted_files}.
    """
    local_archives = download_tgz_archives(bucket_inputs_dir)
    extract_summary = extract_archives_to_input_dir(local_archives, settings.INPUT_DATA_DIR.absolute())
    return {"downloaded": len(local_archives), **extract_summary}
