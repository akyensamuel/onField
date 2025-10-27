# 🚀 Production Deployment Checklist

**Date**: October 27, 2025  
**Target**: Render.com - https://onfieldrecording.onrender.com

---

## ✅ Pre-Deployment Verification

### Code Changes Completed
- [x] Supabase Storage integration (`DataForm/storage.py`, `DataForm/backends.py`)
- [x] Sentry error monitoring configured (`settings.py`)
- [x] Record number auto-generation bug fixed (`DataForm/models.py`)
- [x] Migration 0004 created (`storage_url` field)
- [x] Test suite created (17 tests, all passing)
- [x] Sentry debug endpoint removed from production code
- [x] Documentation created (4 comprehensive guides)

### Files Modified This Session
```
Modified:
- requirements.txt (added 9 packages)
- OnFieldRecording/settings.py (Supabase + Sentry config)
- DataForm/models.py (RecordMedia.storage_url + Record.save())
- OnFieldRecording/urls.py (cleaned up)
- .env.example (updated with new variables)

Created:
- DataForm/storage.py (~200 lines)
- DataForm/backends.py (~120 lines)
- DataForm/migrations/0004_recordmedia_storage_url.py
- DataForm/tests_corrected.py (352 lines, 17 tests)
- SUPABASE_STORAGE_SETUP.md
- SENTRY_SETUP.md
- SENTRY_STATUS_REPORT.md
- TESTING_GUIDE.md
- ITERATION_SUMMARY.md
- DEPLOYMENT_CHECKLIST.md (this file)
- test_sentry.py
- trigger_sentry_url.py
- pytest.ini
```

---

## 📋 Deployment Steps

### Step 1: Push to GitHub ⏳
```bash
cd D:\code\onField
git add .
git commit -m "Add Supabase Storage, Sentry monitoring, fix record_number bug, add test suite"
git push origin main
```

**Verify:**
- Check GitHub repository for new commit
- Verify all files pushed correctly

---

### Step 2: Configure Render Environment Variables ⏳

**Navigate to**: Render Dashboard → OnFieldRecording → Environment

**Required Variables:**
```env
# Critical (MUST be set)
DEBUG=False
ALLOWED_HOSTS=onfieldrecording.onrender.com
SECRET_KEY=<generate-new-production-key>

# Database (should already exist)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
DB_USER=postgres.voilmlhlbdglogddexqb
DB_PASSWORD=f6CJ*VqURR$4tKW
DB_HOST=aws-1-eu-north-1.pooler.supabase.com
DB_PORT=6543

# Sentry Monitoring (NEW)
SENTRY_DSN=https://7056ba16afb5e3f337934fdc7e19bfa3@o4510257691492352.ingest.de.sentry.io/4510257697390672

# Optional: Supabase Storage (if you want cloud storage)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_api_key_here
USE_SUPABASE_STORAGE=True
```

**Security Notes:**
- ⚠️ **Generate NEW SECRET_KEY for production** (never use dev key)
- ✅ Set `DEBUG=False` (critical security requirement)
- ✅ Set correct `ALLOWED_HOSTS`

**Generate New SECRET_KEY:**
```python
# Run in local terminal:
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

### Step 3: Deploy on Render ⏳

Render will automatically deploy when you push to main branch.

**Monitor deployment:**
- Render Dashboard → Logs
- Watch for successful build
- Check for migration execution

**Expected Output:**
```
Building...
Installing dependencies from requirements.txt
Collecting dependencies...
Running migrations...
  Applying DataForm.0004_recordmedia_storage_url... OK
Collecting static files...
170 static files copied
Starting server with Gunicorn...
```

---

### Step 4: Verify Deployment ⏳

#### 4.1 Check Application Health
```bash
# Test homepage
curl https://onfieldrecording.onrender.com/

# Should return 200 OK
```

#### 4.2 Verify Sentry Integration
- Visit: https://sentry.io/organizations/[your-org]/issues/
- Look for any startup errors
- Environment should show: "production"

#### 4.3 Test Core Functionality
- [ ] Login works
- [ ] Dashboard loads
- [ ] Can create operation
- [ ] Can create record (verify record_number auto-generates)
- [ ] Can upload media files
- [ ] Can export data

#### 4.4 Check Database Migration
```bash
# SSH into Render or check logs
python manage.py showmigrations

# Should show:
# DataForm
#  [X] 0001_initial
#  [X] 0002_deletionlog
#  [X] 0003_alter_record_operation
#  [X] 0004_recordmedia_storage_url  ← NEW
```

---

## 🐛 Post-Deployment Testing

### Test Record Number Generation
1. Create a new operation
2. Add a new record
3. Verify `record_number` format: `REC-OP{id}-0001`
4. Add another record
5. Verify sequential: `REC-OP{id}-0002`

### Test Sentry Error Reporting
1. Trigger a test error (intentional)
2. Check Sentry dashboard within 30 seconds
3. Verify error appears with full stack trace
4. Verify environment = "production"

### Test File Uploads
1. Create a record
2. Upload an image
3. Verify image appears
4. If Supabase Storage enabled, check Supabase dashboard

---

## 🔧 Troubleshooting

### Common Issues

**Issue 1: Migration fails on Render**
```
Solution: Run migration manually via Render shell
1. Render Dashboard → Shell
2. python manage.py migrate --fake-initial
```

**Issue 2: Static files not loading**
```
Solution: Collect static files
1. Check STATIC_ROOT in settings.py
2. Run: python manage.py collectstatic --noinput
3. Verify STATIC_URL is accessible
```

**Issue 3: Sentry not capturing errors**
```
Solution: Verify configuration
1. Check SENTRY_DSN environment variable
2. Verify DEBUG=False (Sentry doesn't capture in debug mode by default)
3. Check Sentry project is active
4. Review Sentry quota/rate limits
```

**Issue 4: Record numbers not generating**
```
Solution: Verify migration applied
1. Check DataForm.0004 migration is applied
2. Verify Record.save() method exists in models.py
3. Check database has record_number column
```

**Issue 5: 500 Internal Server Error**
```
Solution: Check logs
1. Render Dashboard → Logs
2. Look for Python traceback
3. Check Sentry dashboard for error details
4. Verify all environment variables set correctly
```

---

## 📊 Success Criteria

### Deployment is successful when:
- ✅ Website loads without errors
- ✅ Users can log in
- ✅ Records can be created with auto-generated numbers
- ✅ Sentry captures and reports errors
- ✅ Static files load correctly
- ✅ Media uploads work
- ✅ Exports generate successfully
- ✅ No migration errors in logs

---

## 🎯 Optional: Supabase Storage Setup

**Only if you want cloud storage for media files:**

### 1. Create Supabase Bucket
1. Go to: https://supabase.com/dashboard
2. Navigate to: Storage
3. Create new bucket: `onfield-media`
4. Set to **Private** (not public)

### 2. Configure RLS Policies
```sql
-- Allow authenticated users to upload
CREATE POLICY "Authenticated users can upload"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'onfield-media');

-- Allow authenticated users to read their uploads
CREATE POLICY "Authenticated users can read"
ON storage.objects FOR SELECT
TO authenticated
USING (bucket_id = 'onfield-media');

-- Allow authenticated users to delete their uploads
CREATE POLICY "Authenticated users can delete"
ON storage.objects FOR DELETE
TO authenticated
USING (bucket_id = 'onfield-media');
```

### 3. Get API Credentials
1. Supabase Dashboard → Settings → API
2. Copy **Project URL** → Set as `SUPABASE_URL`
3. Copy **anon/public key** → Set as `SUPABASE_KEY`

### 4. Add to Render Environment
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
USE_SUPABASE_STORAGE=True
```

### 5. Test Upload
1. Create a record
2. Upload an image
3. Check Supabase Storage dashboard
4. Verify file appears in `onfield-media` bucket

**See SUPABASE_STORAGE_SETUP.md for detailed guide**

---

## 📈 Monitoring

### Set Up Alerts

**Sentry Alerts:**
1. Sentry Dashboard → Alerts
2. Create alert: "New Issue Created"
3. Set notification: Email/Slack
4. Create alert: "Issue Spike" (>10 errors/hour)

**Render Monitoring:**
1. Render Dashboard → Metrics
2. Monitor: Response times, Memory usage, CPU
3. Set up: Health check endpoint

### Regular Checks
- **Daily**: Check Sentry for new errors
- **Weekly**: Review performance metrics
- **Monthly**: Review database size and optimize

---

## 🎉 Rollback Plan

If deployment fails:

```bash
# Option 1: Revert to previous commit
git revert HEAD
git push origin main

# Option 2: Roll back to specific commit
git reset --hard <previous-commit-hash>
git push origin main --force

# Option 3: Use Render's rollback feature
# Render Dashboard → Deployments → Select previous deployment → Redeploy
```

---

## 📝 Post-Deployment Tasks

After successful deployment:

- [ ] Update README.md with new features
- [ ] Notify team about Sentry monitoring
- [ ] Document environment variables in team wiki
- [ ] Schedule user training (if needed)
- [ ] Plan next iteration features (Analytics, Celery, Privacy)

---

## 🚀 Next Session Plan

**Remaining Improvements:**
1. Advanced Analytics with Pandas (Task 4)
2. Celery Background Jobs (Task 5)
3. Privacy & Compliance (Task 6)

**Estimated Time:** 14-20 hours total

---

**Prepared by**: GitHub Copilot  
**Date**: October 27, 2025  
**Status**: Ready for deployment  
**Risk Level**: Low (all features tested locally)
