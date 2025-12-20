"""
Custom storage backend for Vercel Blob Storage.
Handles file uploads to Vercel Blob in production.
"""

import os
from io import BytesIO
from urllib.parse import urljoin

from django.core.files.base import File
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible


@deconstructible
class VercelBlobStorage(Storage):
    """
    Custom storage backend that uses Vercel Blob for file storage.
    Falls back to local filesystem in development.
    """

    def __init__(self):
        self.base_url = os.getenv("BLOB_READ_WRITE_TOKEN", "")
        self.is_production = os.getenv("VERCEL_ENV") in ["production", "preview"]

    def _open(self, name, mode="rb"):
        """
        Retrieve a file from Vercel Blob.
        """
        if not self.is_production:
            # Development: use local filesystem
            from django.core.files.storage import FileSystemStorage

            local_storage = FileSystemStorage()
            return local_storage._open(name, mode)

        try:
            from vercel_blob import get

            blob = get(name)
            return File(BytesIO(blob), name=name)
        except Exception as e:
            raise IOError(f"Error opening file {name} from Vercel Blob: {e}")

    def _save(self, name, content):
        """
        Save a file to Vercel Blob.
        """
        if not self.is_production:
            # Development: use local filesystem
            from django.core.files.storage import FileSystemStorage

            local_storage = FileSystemStorage()
            return local_storage._save(name, content)

        try:
            from vercel_blob import put

            # Read content
            content.seek(0)
            file_data = content.read()

            # Upload to Vercel Blob
            blob = put(pathname=name, body=file_data, options={"access": "public"})

            # Return the pathname (used as reference in database)
            return blob.get("pathname", name)

        except Exception as e:
            raise IOError(f"Error saving file {name} to Vercel Blob: {e}")

    def delete(self, name):
        """
        Delete a file from Vercel Blob.
        """
        if not self.is_production:
            from django.core.files.storage import FileSystemStorage

            local_storage = FileSystemStorage()
            return local_storage.delete(name)

        try:
            from vercel_blob import delete as blob_delete

            blob_delete(name)
        except Exception as e:
            # Don't raise error on delete failure
            print(f"Warning: Could not delete {name} from Vercel Blob: {e}")

    def exists(self, name):
        """
        Check if a file exists in Vercel Blob.
        """
        if not self.is_production:
            from django.core.files.storage import FileSystemStorage

            local_storage = FileSystemStorage()
            return local_storage.exists(name)

        try:
            from vercel_blob import head

            result = head(name)
            return result is not None
        except:
            return False

    def url(self, name):
        """
        Return the URL for accessing the file.
        """
        if not self.is_production:
            from django.core.files.storage import FileSystemStorage

            local_storage = FileSystemStorage()
            return local_storage.url(name)

        # Vercel Blob URLs are in the format:
        # https://[random-id].public.blob.vercel-storage.com/[filename]
        # The exact URL is returned when uploading, but we construct it here
        blob_url = os.getenv("BLOB_URL_PREFIX", "")
        if blob_url:
            return urljoin(blob_url, name)

        # Fallback: assume the file was saved with full URL
        if name.startswith("http"):
            return name

        return f"/media/{name}"

    def size(self, name):
        """
        Return the size of the file.
        """
        if not self.is_production:
            from django.core.files.storage import FileSystemStorage

            local_storage = FileSystemStorage()
            return local_storage.size(name)

        try:
            from vercel_blob import head

            result = head(name)
            return result.get("size", 0) if result else 0
        except:
            return 0

    def get_available_name(self, name, max_length=None):
        """
        Return a filename that's available in the storage.
        Vercel Blob allows overwriting, so we can use the same name.
        """
        return name

    def get_valid_name(self, name):
        """
        Return a valid filename for Vercel Blob.
        """
        # Remove any path components and keep only the filename
        return os.path.basename(name)
