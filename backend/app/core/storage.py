import logging
import os
import boto3
from botocore.exceptions import ClientError
from .config import settings

logger = logging.getLogger(__name__)

# Connect to MinIO
s3 = boto3.client(
    "s3",
    endpoint_url=settings.STORAGE_ENDPOINT,
    aws_access_key_id=settings.STORAGE_ACCESS_KEY,
    aws_secret_access_key=settings.STORAGE_SECRET_KEY,
    region_name=settings.STORAGE_REGION
)

bucket_name = settings.STORAGE_BUCKET

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
    dest_path = f"{user_id}/{task_id}/{file_name}"
    save_file(src_path, dest_path)
    return dest_path

def generate_presigned_url(key: str, expires_in_seconds: int = settings.STORAGE_SIGN_EXPIRE_SECONDS) -> str:
    # Generate a presigned URL for download
    url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket_name, "Key": key},
        ExpiresIn=expires_in_seconds
    )
    return url
