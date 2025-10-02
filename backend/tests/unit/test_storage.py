from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from types import SimpleNamespace

import pytest


class TestDeleteFileOps:
    def test_delete_file_success_and_not_found(self):
        import importlib, sys
        # Import real module and patch on its namespace
        storage = importlib.import_module("app.core.storage")

        s3_mock = MagicMock()
        class FakeClientError(Exception):
            def __init__(self, code: str):
                self.response = {"Error": {"Code": code}}
        with patch.object(storage, "s3", s3_mock), patch.object(storage, "ClientError", FakeClientError):
            # success path
            assert storage.delete_file("a/b/c.txt") is True
            s3_mock.delete_object.assert_called_once()

            s3_mock.reset_mock()
            # not found should return False but not warn (NoSuchKey)
            # Not found should be False and swallowed
            s3_mock.delete_object.side_effect = FakeClientError("NoSuchKey")
            assert storage.delete_file("missing.txt") is False

    def test_delete_files_batch_mixed_results(self):
        import importlib
        storage = importlib.import_module("app.core.storage")

        s3_mock = MagicMock()
        class FakeClientError(Exception):
            def __init__(self, code: str = "Boom"):
                self.response = {"Error": {"Code": code}}
        # First chunk returns some deleted, some errors
        # Use an iterator to yield different responses per call
        side_effects = iter([
            {"Deleted": [{"Key": "k1"}], "Errors": [{"Key": "k2"}]},
            # Make subsequent calls raise a ClientError-like so storage.delete_files catches and counts
            FakeClientError(),
            FakeClientError(),
        ])
        def delete_objects_side_effect(*args, **kwargs):
            res = next(side_effects)
            # Emulate raising on non-dict entries
            if not isinstance(res, dict):
                raise res
            return res
        s3_mock.delete_objects.side_effect = delete_objects_side_effect
        with patch.object(storage, "s3", s3_mock), patch.object(storage, "ClientError", FakeClientError):
            keys = [f"k{i}" for i in range(2005)]  # 3 chunks (1000, 1000, 5)
            summary = storage.delete_files(keys)
            assert summary["requested"] == 2005
            # From first chunk: 1 deleted, 1 error; second chunk exception -> 1000 errors; third chunk exception -> 5 errors
            assert summary["deleted"] == 1
            assert summary["errors"] == 1 + 1000 + 5


class TestInitializationHelpers:
    def test_list_and_download_and_extract(self, tmp_path):
        import importlib
        storage = importlib.import_module("app.core.storage")

        # Fake list returns two tgz keys
        with patch.object(storage, "_list_tgz_keys_under_prefix", return_value=["inputs/a.tgz", "inputs/b.tgz"]):
            # Patch s3 client methods
            s3_mock = MagicMock()
            with patch.object(storage, "s3", s3_mock):
                # Make download create local dummy files and validate called
                def fake_download(bucket, key, local):
                    with open(local, "wb") as f:
                        f.write(b"dummy")
                s3_mock.download_file.side_effect = fake_download

                # Ensure os.path.exists and os.remove are exercised safely
                with patch.object(storage.os.path, "exists", return_value=False):
                    files = storage.download_tgz_archives("inputs", local_cache_dir=str(tmp_path))
                assert len(files) == 2
                assert all(p.startswith(str(tmp_path)) for p in files)

        # Now test extraction summarizer — patch the extractor to simulate extracted entries
        with patch.object(storage, "_safe_extract_tgz", side_effect=[["x/1", "x/2"], ["y/1"]]):
            summary = storage.extract_archives_to_input_dir([str(tmp_path/"a.tgz"), str(tmp_path/"b.tgz")], str(tmp_path/"out"))
            assert summary == {"archives": 2, "extracted_files": 3}


class TestMoreStorage:
    def test_generate_presigned_url(self):
        import importlib
        storage = importlib.import_module("app.core.storage")
        s3_mock = MagicMock()
        s3_mock.generate_presigned_url.return_value = "http://signed"
        with patch.object(storage, "s3", s3_mock):
            url = storage.generate_presigned_url("outputs/1/2/file.tif", expires_in_seconds=123)
            assert url == "http://signed"
            s3_mock.generate_presigned_url.assert_called_once()

    def test_list_tgz_keys_under_prefix(self):
        import importlib
        storage = importlib.import_module("app.core.storage")

        class FakePaginator:
            def paginate(self, **kwargs):
                # Ensure prefix ends with '/'
                assert kwargs["Prefix"].endswith("/")
                return [
                    {"Contents": [{"Key": "inputs/a.tgz"}, {"Key": "inputs/skip.txt"}]},
                    {"Contents": [{"Key": "inputs/b.tgz"}]},
                ]

        s3_mock = MagicMock()
        s3_mock.get_paginator.return_value = FakePaginator()
        with patch.object(storage, "s3", s3_mock):
            keys = storage._list_tgz_keys_under_prefix("inputs")
            assert keys == ["inputs/a.tgz", "inputs/b.tgz"]

    def test_safe_extract_tgz_skips_bad_members(self, tmp_path):
        import importlib, io, tarfile, os
        storage = importlib.import_module("app.core.storage")

        # Build a tar.gz containing:
        # - a safe file 'dir/file.txt'
        # - a directory 'dir/sub'
        # - a symlink 'dir/l' (should be skipped)
        # - a traversal '../evil.txt' (should be skipped)
        tar_path = tmp_path / "arch.tgz"
        with tarfile.open(tar_path, "w:gz") as tf:
            # safe file
            data = io.BytesIO(b"hello")
            info = tarfile.TarInfo(name="dir/file.txt")
            info.size = len(data.getbuffer())
            tf.addfile(info, data)

            # directory
            d = tarfile.TarInfo(name="dir/sub")
            d.type = tarfile.DIRTYPE
            tf.addfile(d)

            # symlink
            sym = tarfile.TarInfo(name="dir/l")
            sym.type = tarfile.SYMTYPE
            sym.linkname = "file.txt"
            tf.addfile(sym)

            # traversal
            evil = tarfile.TarInfo(name="../evil.txt")
            evil.size = 0
            tf.addfile(evil, io.BytesIO(b""))

        out_dir = tmp_path / "out"
        extracted = storage._safe_extract_tgz(str(tar_path), str(out_dir))
        # Should include created directory 'dir/sub' and file 'dir/file.txt', but not symlink or traversal
        assert any(p.endswith("dir/sub") for p in extracted)
        assert any(p.endswith("dir/file.txt") for p in extracted)
        assert not (out_dir / "evil.txt").exists()
        assert not (out_dir / "dir" / "l").exists()

    def test_initialize_input_dir_from_bucket(self, tmp_path):
        import importlib
        storage = importlib.import_module("app.core.storage")
        with patch.object(storage, "download_tgz_archives", return_value=[str(tmp_path/"a.tgz"), str(tmp_path/"b.tgz")]), \
             patch.object(storage, "extract_archives_to_input_dir", return_value={"archives": 2, "extracted_files": 3}), \
             patch.object(storage.settings, "INPUT_DATA_DIR", tmp_path):
            summary = storage.initialize_input_dir_from_bucket()
            assert summary == {"downloaded": 2, "archives": 2, "extracted_files": 3}
