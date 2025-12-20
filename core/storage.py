"""
Custom storage backend for Vercel Blob Storage.
Handles file uploads to Vercel Blob in production.
"""

import os
from io import BytesIO
from urllib.parse import urljoin

import requests
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
        self.token = os.getenv("BLOB_READ_WRITE_TOKEN", "")
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
            # Use the stored URL to download the file
            if name.startswith("http"):
                response = requests.get(name)
                response.raise_for_status()
                return File(BytesIO(response.content), name=name)
            else:
                # File not found or invalid URL
                raise IOError(f"Invalid file reference: {name}")
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
            # Read content
            content.seek(0)
            file_data = content.read()

            # Upload to Vercel Blob using PUT with Authorization header
            url = f"https://blob.vercel-storage.com/{name}"

            response = requests.put(
                url,
                data=file_data,
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/octet-stream",
                },
            )
            response.raise_for_status()

            result = response.json()

            # Return the full URL - we'll store this in the database
            return result.get("url", name)

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
            # Vercel Blob delete requires the full URL
            if not name.startswith("http"):
                return

            url = "https://blob.vercel-storage.com/delete"
            headers = {
                "authorization": f"Bearer {self.token}",
            }

            response = requests.post(
                url,
                headers=headers,
                json={"urls": [name]},
            )
            response.raise_for_status()
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

        # In production, assume URL-based files exist
        return name.startswith("http")

    def url(self, name):
        """
        Return the URL for accessing the file.
        """
        if not self.is_production:
            from django.core.files.storage import FileSystemStorage

            local_storage = FileSystemStorage()
            return local_storage.url(name)

        # If name is already a full URL, return it
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
            if name.startswith("http"):
                response = requests.head(name)
                return int(response.headers.get("content-length", 0))
            return 0
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
