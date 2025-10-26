"""
Script to create admin UserProfile for the superuser
Run this after creating the superuser with: python create_admin_profile.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'OnFieldRecording.settings')
django.setup()

from django.contrib.auth.models import User
from DataForm.models import UserProfile

# Get the admin user
try:
    admin_user = User.objects.get(username='admin')
    
    # Check if profile already exists
    if hasattr(admin_user, 'profile'):
        print(f"✓ UserProfile already exists for '{admin_user.username}'")
        print(f"  Role: {admin_user.profile.role}")
        print(f"  Phone: {admin_user.profile.phone_number or 'Not set'}")
    else:
        # Create admin profile
        profile = UserProfile.objects.create(
            user=admin_user,
            role='admin',
            phone_number=''  # Can be updated later in admin panel
        )
        print(f"✓ Created admin UserProfile for '{admin_user.username}'")
        print(f"  Role: {profile.role}")
        print(f"  Email: {admin_user.email}")
        print("\nYou can now log in at: http://127.0.0.1:8000/")
        print("  Username: admin")
        print("  Password: (the password you just set)")
        
except User.DoesNotExist:
    print("✗ Error: User 'admin' not found!")
    print("  Please create the superuser first with:")
    print("  python manage.py createsuperuser --username admin --email admin@onfield.com")
except Exception as e:
    print(f"✗ Error: {e}")
