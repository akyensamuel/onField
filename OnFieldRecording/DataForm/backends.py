"""
Custom Django Storage Backend for Supabase Storage
"""
from django.core.files.storage import Storage
from django.core.files.base import File, ContentFile
from django.conf import settings
from django.utils.deconstruct import deconstructible
from .storage import get_storage
import os
from datetime import datetime


@deconstructible
class SupabaseMediaStorage(Storage):
    """
    Django storage backend that uses Supabase Storage
    Falls back to local storage if Supabase is not configured
    """
    
    def __init__(self):
        self.supabase_storage = get_storage()
        self.use_supabase = self.supabase_storage.is_configured()
        
        if not self.use_supabase:
            # Fallback to local storage
            from django.core.files.storage import FileSystemStorage
            self.fallback_storage = FileSystemStorage(
                location=settings.MEDIA_ROOT,
                base_url=settings.MEDIA_URL
            )
    
    def _save(self, name, content):
        """
        Save file to Supabase Storage or local filesystem
        
        Args:
            name: File path
            content: File content
        
        Returns:
            str: File path
        """
        if self.use_supabase:
            # Upload to Supabase
            result = self.supabase_storage.upload_file(content, name)
            if result['success']:
                return name
            else:
                # If upload fails, fall back to local storage
                if hasattr(self, 'fallback_storage'):
                    return self.fallback_storage._save(name, content)
                raise IOError(f"Failed to upload to Supabase: {result['error']}")
        else:
            # Use local storage
            return self.fallback_storage._save(name, content)
    
    def _open(self, name, mode='rb'):
        """
        Open file from Supabase Storage or local filesystem
        
        Note: For Supabase, we return the URL instead of downloading the file
        """
        if self.use_supabase:
            # For now, we don't support reading from Supabase in Django
            # Files are served via public URLs
            raise NotImplementedError("Reading from Supabase storage is not yet supported")
        else:
            return self.fallback_storage._open(name, mode)
    
    def delete(self, name):
        """Delete file from storage"""
        if self.use_supabase:
            result = self.supabase_storage.delete_file(name)
            if not result['success']:
                # If delete fails, try fallback
                if hasattr(self, 'fallback_storage'):
                    self.fallback_storage.delete(name)
        else:
            self.fallback_storage.delete(name)
    
    def exists(self, name):
        """Check if file exists"""
        if self.use_supabase:
            # For Supabase, we'll assume files exist after upload
            # This could be enhanced with actual existence checking
            return False  # Always return False to avoid conflicts
        else:
            return self.fallback_storage.exists(name)
    
    def url(self, name):
        """
        Get public URL for file
        """
        if self.use_supabase:
            url = self.supabase_storage.get_public_url(name)
            return url if url else f"/media/{name}"  # Fallback to local
        else:
            return self.fallback_storage.url(name)
    
    def size(self, name):
        """Get file size"""
        if self.use_supabase:
            # Size checking not implemented for Supabase
            return 0
        else:
            return self.fallback_storage.size(name)
    
    def path(self, name):
        """
        Get local filesystem path
        Only works for local storage
        """
        if self.use_supabase:
            raise NotImplementedError("Supabase storage doesn't use local paths")
        else:
            return self.fallback_storage.path(name)
    
    def get_accessed_time(self, name):
        """Get last accessed time"""
        if self.use_supabase:
            return datetime.now()
        else:
            return self.fallback_storage.get_accessed_time(name)
    
    def get_created_time(self, name):
        """Get creation time"""
        if self.use_supabase:
            return datetime.now()
        else:
            return self.fallback_storage.get_created_time(name)
    
    def get_modified_time(self, name):
        """Get last modified time"""
        if self.use_supabase:
            return datetime.now()
        else:
            return self.fallback_storage.get_modified_time(name)
