"""Tests for Storage Drivers (Local and GCS)."""

import asyncio
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from backend.services.drivers.gcs_file_driver import GCSFileDriver
from backend.services.drivers.local_file_driver import LocalFileDriver


class TestLocalFileDriver(unittest.TestCase):
    """Integration settings for LocalFileDriver."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.driver = LocalFileDriver(base_path=self.test_dir, base_url="http://test.com/files")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_save_and_read(self):
        async def run():
            content = b"Hello world"
            path = "test.txt"

            # Save
            saved_path = await self.driver.save(path, content)
            self.assertTrue(saved_path.endswith("test.txt"))

            # Read
            read_content = await self.driver.read(path)
            self.assertEqual(read_content, content)

            # Exists
            exists = await self.driver.exists(path)
            self.assertTrue(exists)

        asyncio.run(run())

    def test_delete(self):
        async def run():
            path = "delete_me.txt"
            await self.driver.save(path, b"content")

            self.assertTrue(await self.driver.exists(path))

            deleted = await self.driver.delete(path)
            self.assertTrue(deleted)
            self.assertFalse(await self.driver.exists(path))

            # Delete non-existent
            deleted_again = await self.driver.delete(path)
            self.assertFalse(deleted_again)

        asyncio.run(run())

    def test_save_string(self):
        async def run():
            path = "string.txt"
            content = "Hello String"
            await self.driver.save(path, content)

            read_bytes = await self.driver.read(path)
            self.assertEqual(read_bytes.decode("utf-8"), content)

        asyncio.run(run())

    def test_nested_dir(self):
        async def run():
            path = "subdir/nested/file.txt"
            await self.driver.save(path, b"nested")
            self.assertTrue(await self.driver.exists(path))

        asyncio.run(run())

    def test_get_url(self):
        async def run():
            url = await self.driver.get_url("foo/bar.txt")
            self.assertEqual(url, "http://test.com/files/foo/bar.txt")

        asyncio.run(run())


class TestGCSFileDriver(unittest.TestCase):
    """Unit tests for GCSFileDriver with mocks."""

    def setUp(self):
        self.driver = GCSFileDriver(bucket_name="test-bucket")

    @patch("backend.services.drivers.gcs_file_driver.storage.Client")
    def test_save(self, mock_client_cls):
        async def run():
            # Setup Mock
            mock_client = MagicMock()
            mock_bucket = MagicMock()
            mock_blob = MagicMock()

            mock_client_cls.return_value = mock_client
            mock_client.bucket.return_value = mock_bucket
            mock_bucket.blob.return_value = mock_blob

            # Action
            path = "gcs_test.txt"
            content = b"gcs content"
            result = await self.driver.save(path, content)

            # Verification
            mock_client.bucket.assert_called_with("test-bucket")
            mock_bucket.blob.assert_called_with(path)
            mock_blob.upload_from_string.assert_called_with(content, content_type="application/octet-stream")

            self.assertEqual(result, "gs://test-bucket/gcs_test.txt")

        asyncio.run(run())

    @patch("backend.services.drivers.gcs_file_driver.storage.Client")
    def test_read(self, mock_client_cls):
        async def run():
            mock_client = MagicMock()
            mock_bucket = MagicMock()
            mock_blob = MagicMock()

            mock_client_cls.return_value = mock_client
            mock_client.bucket.return_value = mock_bucket
            mock_bucket.blob.return_value = mock_blob
            mock_blob.download_as_bytes.return_value = b"gcs data"

            data = await self.driver.read("file.txt")
            self.assertEqual(data, b"gcs data")

        asyncio.run(run())

    @patch("backend.services.drivers.gcs_file_driver.storage.Client")
    def test_delete(self, mock_client_cls):
        async def run():
            mock_client = MagicMock()
            mock_bucket = MagicMock()
            mock_blob = MagicMock()

            mock_client_cls.return_value = mock_client
            mock_client.bucket.return_value = mock_bucket
            mock_bucket.blob.return_value = mock_blob
            mock_blob.exists.return_value = True

            deleted = await self.driver.delete("file.txt")
            self.assertTrue(deleted)
            mock_blob.delete.assert_called()

        asyncio.run(run())

    @patch("backend.services.drivers.gcs_file_driver.storage.Client")
    def test_exists(self, mock_client_cls):
        async def run():
            mock_client = MagicMock()
            mock_bucket = MagicMock()
            mock_blob = MagicMock()

            mock_client_cls.return_value = mock_client
            mock_client.bucket.return_value = mock_bucket
            mock_bucket.blob.return_value = mock_blob
            mock_blob.exists.return_value = True

            exists = await self.driver.exists("file.txt")
            self.assertTrue(exists)

        asyncio.run(run())
