# Supabase Storage Setup Guide
**OnField Recording System - Cloud Media Storage**  
**Date**: October 26, 2025

---

## 🎯 Overview

This guide will help you configure Supabase Storage for storing user-uploaded photos and media files. This replaces local filesystem storage with cloud-based storage.

---

## Why Supabase Storage?

### Benefits
✅ **Same Provider**: Already using Supabase for PostgreSQL database  
✅ **Automatic Backups**: Files are backed up automatically  
✅ **Scalable**: No storage limits on your server  
✅ **CDN Delivery**: Fast file access globally  
✅ **Secure**: Private buckets with access controls  
✅ **Cost-Effective**: Free tier includes 1GB storage  

### vs Local Storage
| Feature | Local Storage | Supabase Storage |
|---------|--------------|------------------|
| **Server Restarts** | ❌ Files lost | ✅ Files persist |
| **Multiple Servers** | ❌ Not shared | ✅ Centralized |
| **Backups** | ⚠️ Manual | ✅ Automatic |
| **Scaling** | ❌ Limited by disk | ✅ Unlimited |
| **Cost** | Free (uses disk) | Free tier + paid |

---

## Step 1: Create Supabase Storage Bucket

### 1.1 Access Supabase Dashboard

1. Go to https://app.supabase.com/
2. Select your project (same one with your database)
3. Click **Storage** in the left sidebar

### 1.2 Create New Bucket

1. Click **"New bucket"** button
2. **Name**: `onfield-media`
3. **Public bucket**: Toggle **OFF** (keep it private)
4. **File size limit**: 5MB (optional)
5. **Allowed MIME types**: Leave empty or add: `image/jpeg, image/png, image/gif`
6. Click **"Create bucket"**

### 1.3 Configure Bucket Policies

After creating the bucket, you need to set up access policies:

1. Click on the `onfield-media` bucket
2. Click **"Policies"** tab
3. Click **"New policy"**

**Policy 1: Allow Authenticated Uploads**
```sql
CREATE POLICY "Allow authenticated uploads"
ON storage.objects
FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'onfield-media'
);
```

**Policy 2: Allow Authenticated Reads**
```sql
CREATE POLICY "Allow authenticated reads"
ON storage.objects
FOR SELECT
TO authenticated
USING (
  bucket_id = 'onfield-media'
);
```

**Policy 3: Allow Authenticated Deletes**
```sql
CREATE POLICY "Allow authenticated deletes"
ON storage.objects
FOR DELETE
TO authenticated
USING (
  bucket_id = 'onfield-media'
);
```

---

## Step 2: Get Supabase Credentials

### 2.1 Get Project URL

1. In Supabase Dashboard, go to **Settings** → **API**
2. Copy the **Project URL** (e.g., `https://abcdefgh.supabase.co`)

### 2.2 Get API Key

1. In the same **API** page
2. Copy the **anon/public** key (it's a long JWT token)

⚠️ **Note**: Use the `anon` key, not the `service_role` key!

---

## Step 3: Configure Your Application

### 3.1 Update `.env` File

Add these lines to `d:\code\onField\.env`:

```properties
# Supabase Storage Configuration
USE_SUPABASE_STORAGE=True
SUPABASE_URL=https://voilmlhlbdglogddexqb.supabase.co
SUPABASE_KEY=your-supabase-anon-key-here
SUPABASE_STORAGE_BUCKET=onfield-media
```

**Replace**:
- `SUPABASE_URL`: Your actual project URL from Step 2.1
- `SUPABASE_KEY`: Your anon key from Step 2.2

### 3.2 For Render.com Deployment

Add the same environment variables in Render dashboard:

1. Go to https://dashboard.render.com/
2. Select your service
3. Click **Environment** tab
4. Add:
   - `USE_SUPABASE_STORAGE=True`
   - `SUPABASE_URL=https://voilmlhlbdglogddexqb.supabase.co`
   - `SUPABASE_KEY=your-anon-key`
   - `SUPABASE_STORAGE_BUCKET=onfield-media`
5. Click **"Save Changes"**

---

## Step 4: Install Dependencies

### 4.1 Install Supabase Python Client

```bash
pip install supabase storage3
```

These are already in `requirements.txt`, so on Render they'll install automatically.

### 4.2 Run Migration

```bash
cd OnFieldRecording
python manage.py migrate
```

This adds the `storage_url` field to the `RecordMedia` model.

---

## Step 5: Test the Integration

### 5.1 Test Upload

1. Log in to your application
2. Create a new record
3. Upload a photo
4. Save the record

### 5.2 Verify in Supabase

1. Go to Supabase Dashboard → **Storage**
2. Click on `onfield-media` bucket
3. You should see your uploaded file in:
   ```
   records/operation_{id}/{record_number}/{timestamp}_{record_id}.jpg
   ```

### 5.3 Verify URL

1. In your application, view the record
2. The photo should display correctly
3. Right-click the photo → "Open in new tab"
4. URL should look like:
   ```
   https://voilmlhlbdglogddexqb.supabase.co/storage/v1/object/public/onfield-media/records/...
   ```

---

## How It Works

### Upload Flow

```
1. User uploads photo in record form
   ↓
2. Django receives file
   ↓
3. SupabaseMediaStorage backend processes it
   ↓
4. File uploaded to Supabase Storage bucket
   ↓
5. Public URL generated and saved in database
   ↓
6. Photo displays using Supabase CDN URL
```

### File Organization

```
onfield-media/
├── records/
│   ├── operation_1/
│   │   ├── JOB0001/
│   │   │   ├── 20251026_143000_123.jpg
│   │   │   └── 20251026_143015_123.jpg
│   │   └── JOB0002/
│   │       └── 20251026_144000_124.jpg
│   └── operation_2/
│       └── JOB0001/
│           └── 20251026_150000_125.jpg
```

---

## Fallback Behavior

### If Supabase Not Configured

The system automatically falls back to local storage if:
- `USE_SUPABASE_STORAGE=False`
- `SUPABASE_URL` or `SUPABASE_KEY` not set
- Connection to Supabase fails

**Fallback Mode**:
- Files saved to `OnFieldRecording/media/` folder
- URLs use `/media/` prefix
- Works offline for development

---

## Migration from Local to Supabase

### If You Have Existing Local Files

**Option 1: Manual Upload** (Small number of files)
1. Go to Supabase Dashboard → Storage → onfield-media
2. Click "Upload file"
3. Select files from your local `media/` folder
4. Upload to matching paths

**Option 2: Bulk Migration Script** (Many files)

Create `migrate_media.py`:
```python
import os
from django.core.management.base import BaseCommand
from DataForm.models import RecordMedia
from DataForm.storage import get_storage

class Command(BaseCommand):
    def handle(self, *args, **options):
        storage = get_storage()
        
        for media in RecordMedia.objects.all():
            if media.image and os.path.exists(media.image.path):
                with open(media.image.path, 'rb') as f:
                    result = storage.upload_file(f, media.image.name)
                    if result['success']:
                        media.storage_url = result['url']
                        media.save()
                        print(f"Migrated: {media.image.name}")
```

Run: `python manage.py migrate_media`

---

## Troubleshooting

### Issue: "Supabase storage not configured"

**Cause**: Environment variables not set  
**Fix**: Add `SUPABASE_URL`, `SUPABASE_KEY`, and `USE_SUPABASE_STORAGE=True` to `.env`

### Issue: "Failed to upload to Supabase"

**Causes**:
1. Invalid API key
2. Bucket doesn't exist
3. Bucket policies not configured

**Fix**:
1. Verify API key is correct (anon key, not service_role)
2. Check bucket name matches `.env` setting
3. Add storage policies (see Step 1.3)

### Issue: "Image not displaying"

**Cause**: Bucket is private but policies not set  
**Fix**: Add storage policies for authenticated users

### Issue: "File too large"

**Cause**: File exceeds 5MB limit  
**Fix**:
1. In `settings.py`: Increase `FILE_UPLOAD_MAX_MEMORY_SIZE`
2. In Supabase: Increase bucket file size limit

---

## Cost Estimation

### Supabase Free Tier
- **Storage**: 1GB included
- **Bandwidth**: 2GB/month
- **API Requests**: Unlimited

### Estimated Usage
- **Average photo**: 500KB
- **Photos per month**: 1000
- **Total storage**: ~500MB
- **Cost**: **FREE** (within free tier)

### Paid Plan (if needed)
- **Pro Plan**: $25/month
- **Includes**: 100GB storage, 250GB bandwidth
- **Additional storage**: $0.021/GB/month

---

## Security Best Practices

### ✅ Do's
- ✅ Use `anon` key (public, safe to expose)
- ✅ Keep bucket **private** (not public)
- ✅ Set up Row Level Security policies
- ✅ Validate file types before upload
- ✅ Limit file sizes (5MB)

### ❌ Don'ts
- ❌ Don't use `service_role` key in client code
- ❌ Don't make bucket public (unless intentional)
- ❌ Don't skip policies (allows anyone to upload)
- ❌ Don't store sensitive data without encryption

---

## Monitoring Storage Usage

### Check Storage Size

1. Go to Supabase Dashboard → **Settings** → **Usage**
2. Look at **Storage** section
3. See total size and file count

### Set Up Alerts

1. Go to **Settings** → **Billing**
2. Set storage threshold alerts (e.g., 80% of quota)
3. Get email notifications

---

## Alternative: AWS S3

If you prefer AWS S3 instead:

### Install
```bash
pip install boto3 django-storages
```

### Configure
```properties
# .env
USE_S3=True
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_STORAGE_BUCKET_NAME=onfield-media
AWS_S3_REGION_NAME=us-east-1
```

### Settings
```python
# settings.py
if config('USE_S3', default=False, cast=bool):
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
```

---

## Summary

### What You've Accomplished
✅ Cloud storage for photos (no more local files)  
✅ Automatic backups via Supabase  
✅ Scalable solution for production  
✅ Fallback to local storage if needed  
✅ Organized file structure  
✅ Secure private bucket with policies  

### Next Steps
1. Configure Supabase bucket (5 min)
2. Add environment variables (2 min)
3. Run migration (1 min)
4. Test upload (2 min)
5. Deploy to Render (auto)

**Total Setup Time**: ~10-15 minutes

---

**Status**: Ready for Production 🚀  
**Complexity**: Low  
**Impact**: High (production-ready media storage)
