"""
Supabase Storage Integration for OnField Recording System
Handles file uploads to Supabase Storage bucket
"""
import os
from io import BytesIO
from decouple import config
from supabase import create_client, Client
from django.core.files.uploadedfile import InMemoryUploadedFile
import logging

logger = logging.getLogger(__name__)


class SupabaseStorage:
    """
    Wrapper for Supabase Storage operations
    """
    
    def __init__(self):
        """Initialize Supabase client"""
        self.url = config('SUPABASE_URL', default='')
        self.key = config('SUPABASE_KEY', default='')
        self.bucket_name = config('SUPABASE_STORAGE_BUCKET', default='onfield-media')
        
        if not self.url or not self.key:
            logger.warning("Supabase credentials not configured. Using local storage.")
            self.client = None
        else:
            try:
                self.client: Client = create_client(self.url, self.key)
                logger.info(f"Supabase storage initialized for bucket: {self.bucket_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                self.client = None
    
    def is_configured(self):
        """Check if Supabase storage is properly configured"""
        return self.client is not None
    
    def upload_file(self, file, path):
        """
        Upload a file to Supabase Storage
        
        Args:
            file: Django UploadedFile object or file-like object
            path: Path within the bucket (e.g., 'records/2024/photo.jpg')
        
        Returns:
            dict: {'success': bool, 'url': str, 'error': str}
        """
        if not self.is_configured():
            return {
                'success': False,
                'url': None,
                'error': 'Supabase storage not configured'
            }
        
        try:
            # Read file content
            if isinstance(file, InMemoryUploadedFile):
                file_content = file.read()
                file.seek(0)  # Reset file pointer
            else:
                file_content = file.read()
            
            # Upload to Supabase Storage
            response = self.client.storage.from_(self.bucket_name).upload(
                path=path,
                file=file_content,
                file_options={"content-type": self._get_content_type(file)}
            )
            
            # Get public URL
            public_url = self.client.storage.from_(self.bucket_name).get_public_url(path)
            
            logger.info(f"File uploaded successfully: {path}")
            return {
                'success': True,
                'url': public_url,
                'path': path,
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Failed to upload file to Supabase: {e}")
            return {
                'success': False,
                'url': None,
                'error': str(e)
            }
    
    def delete_file(self, path):
        """
        Delete a file from Supabase Storage
        
        Args:
            path: Path within the bucket
        
        Returns:
            dict: {'success': bool, 'error': str}
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': 'Supabase storage not configured'
            }
        
        try:
            self.client.storage.from_(self.bucket_name).remove([path])
            logger.info(f"File deleted successfully: {path}")
            return {'success': True, 'error': None}
            
        except Exception as e:
            logger.error(f"Failed to delete file from Supabase: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_public_url(self, path):
        """
        Get public URL for a file
        
        Args:
            path: Path within the bucket
        
        Returns:
            str: Public URL or None
        """
        if not self.is_configured():
            return None
        
        try:
            return self.client.storage.from_(self.bucket_name).get_public_url(path)
        except Exception as e:
            logger.error(f"Failed to get public URL: {e}")
            return None
    
    def list_files(self, prefix=''):
        """
        List files in a folder
        
        Args:
            prefix: Folder prefix (e.g., 'records/2024/')
        
        Returns:
            list: List of file objects
        """
        if not self.is_configured():
            return []
        
        try:
            files = self.client.storage.from_(self.bucket_name).list(prefix)
            return files
        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            return []
    
    def _get_content_type(self, file):
        """Determine content type from file"""
        if hasattr(file, 'content_type'):
            return file.content_type
        
        # Default content types based on extension
        ext = os.path.splitext(getattr(file, 'name', ''))[1].lower()
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.pdf': 'application/pdf',
            '.mp4': 'video/mp4',
        }
        return content_types.get(ext, 'application/octet-stream')
    
    def create_bucket_if_not_exists(self):
        """
        Create the storage bucket if it doesn't exist
        Note: This requires admin privileges
        """
        if not self.is_configured():
            return False
        
        try:
            # List buckets to check if ours exists
            buckets = self.client.storage.list_buckets()
            bucket_names = [b['name'] for b in buckets]
            
            if self.bucket_name not in bucket_names:
                # Create bucket
                self.client.storage.create_bucket(
                    self.bucket_name,
                    options={"public": False}  # Private bucket
                )
                logger.info(f"Created storage bucket: {self.bucket_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create bucket: {e}")
            return False


# Singleton instance
_storage_instance = None

def get_storage():
    """Get or create Supabase storage instance"""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = SupabaseStorage()
    return _storage_instance
