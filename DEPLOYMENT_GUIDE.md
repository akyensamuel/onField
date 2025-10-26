# Production Deployment Checklist
**OnField Recording System**  
**Date**: October 26, 2025

---

## 🚀 Production Deployment - Step by Step

---

## Part 1: Environment Configuration

### Step 1.1: Generate New SECRET_KEY

**Run this command:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Copy the output** (looks like: `django-insecure-xyz123...`)

### Step 1.2: Update Your `.env` File

Open `d:\code\onField\.env` and make these changes:

```properties
# ============================================
# CRITICAL: Change these for production
# ============================================
SECRET_KEY=<paste-the-new-key-you-just-generated>
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,your-server-ip

# ============================================
# Database (already configured - no changes needed)
# ============================================
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
DB_USER=postgres.voilmlhlbdglogddexqb
DB_PASSWORD=f6CJ*VqURR$4tKW
DB_HOST=aws-1-eu-north-1.pooler.supabase.com
DB_PORT=6543

# ============================================
# Security (enable ONLY if you have HTTPS/SSL)
# ============================================
# Uncomment these ONLY after SSL is configured:
# CSRF_COOKIE_SECURE=True
# SESSION_COOKIE_SECURE=True
# SECURE_SSL_REDIRECT=True
# SECURE_HSTS_SECONDS=31536000
# SECURE_HSTS_INCLUDE_SUBDOMAINS=True
```

**⚠️ IMPORTANT**: 
- Replace `your-domain.com` with your actual domain
- If using an IP address, add it to ALLOWED_HOSTS
- Keep `DEBUG=False` in production

---

## Part 2: Static Files

### Step 2.1: Collect Static Files

```bash
cd OnFieldRecording
python manage.py collectstatic --noinput
```

This will create a `staticfiles` folder with all CSS, JS, and images.

### Step 2.2: Configure Static File Serving

**Option A: Using WhiteNoise (Recommended for simple deployments)**

1. Install WhiteNoise:
```bash
pip install whitenoise
```

2. Add to `requirements.txt`:
```
whitenoise==6.6.0
```

3. Your `settings.py` should have this in MIDDLEWARE (add if missing):
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this line
    # ... other middleware
]
```

**Option B: Using Nginx/Apache**
- Configure your web server to serve `/static/` from the `staticfiles` folder
- Configure your web server to serve `/media/` from the `media` folder

---

## Part 3: Media Files (User Uploads)

### ⚠️ Current State: Local Storage (Not Production-Ready)

Your media files are currently saved to the local `media/` folder. This works for testing but has issues in production:
- Files lost if server restarts
- Doesn't work with multiple servers (load balancing)
- No backups

### Recommended: Use Cloud Storage

**Option A: Supabase Storage (Easiest - same provider as your database)**

1. Install package:
```bash
pip install supabase
```

2. Add to `.env`:
```properties
SUPABASE_URL=https://voilmlhlbdglogddexqb.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_STORAGE_BUCKET=onfield-media
```

3. Create storage bucket in Supabase dashboard:
   - Go to https://app.supabase.com/
   - Select your project
   - Storage → New Bucket
   - Name: `onfield-media`
   - Public: No (private)

**Option B: AWS S3 (Most popular)**

1. Install package:
```bash
pip install boto3 django-storages
```

2. Add to `.env`:
```properties
USE_S3=True
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=onfield-media
AWS_S3_REGION_NAME=us-east-1
```

**For MVP/Testing**: You can skip cloud storage initially and use local storage, but plan to migrate soon.

---

## Part 4: Web Server Setup

### Option 1: Deploy to Render.com (Easiest)

1. **Create Account**: https://render.com/

2. **Create New Web Service**:
   - Connect your GitHub repo
   - Choose "Web Service"
   - Build Command: `pip install -r requirements.txt && python OnFieldRecording/manage.py collectstatic --noinput`
   - Start Command: `cd OnFieldRecording && gunicorn OnFieldRecording.wsgi:application`

3. **Add Environment Variables** in Render dashboard:
   - All variables from your `.env` file
   - Add: `PYTHON_VERSION=3.13`

4. **Install Gunicorn**:
```bash
pip install gunicorn
echo "gunicorn==21.2.0" >> requirements.txt
```

### Option 2: Deploy to Railway.app (Also Easy)

1. **Create Account**: https://railway.app/

2. **New Project**:
   - Deploy from GitHub
   - Railway auto-detects Django

3. **Add Environment Variables**:
   - Copy all from your `.env`

4. **Configure**:
   - Build command: `pip install -r requirements.txt`
   - Start command: `cd OnFieldRecording && gunicorn OnFieldRecording.wsgi:application`

### Option 3: Deploy to Your Own Server (Ubuntu/Nginx)

**Prerequisites:**
- Ubuntu 22.04 server
- Root or sudo access
- Domain pointing to server IP

**Quick Setup:**

```bash
# 1. Install dependencies
sudo apt update
sudo apt install python3-pip python3-venv nginx

# 2. Create user and directory
sudo useradd -m -s /bin/bash onfield
sudo mkdir -p /var/www/onfield
sudo chown onfield:onfield /var/www/onfield

# 3. Clone your repository
cd /var/www/onfield
git clone https://github.com/akyensamuel/onField.git .

# 4. Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Create .env file
nano .env  # Paste your production settings

# 6. Collect static files
cd OnFieldRecording
python manage.py collectstatic --noinput

# 7. Install Gunicorn
pip install gunicorn

# 8. Create systemd service
sudo nano /etc/systemd/system/onfield.service
```

**Service file content:**
```ini
[Unit]
Description=OnField Recording System
After=network.target

[Service]
User=onfield
Group=onfield
WorkingDirectory=/var/www/onfield/OnFieldRecording
Environment="PATH=/var/www/onfield/venv/bin"
ExecStart=/var/www/onfield/venv/bin/gunicorn --workers 3 --bind unix:/var/www/onfield/onfield.sock OnFieldRecording.wsgi:application

[Install]
WantedBy=multi-user.target
```

**Start service:**
```bash
sudo systemctl start onfield
sudo systemctl enable onfield
sudo systemctl status onfield
```

**Configure Nginx:**
```bash
sudo nano /etc/nginx/sites-available/onfield
```

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /var/www/onfield/OnFieldRecording/staticfiles/;
    }
    
    location /media/ {
        alias /var/www/onfield/OnFieldRecording/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/onfield/onfield.sock;
    }
}
```

**Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/onfield /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

**Setup SSL with Let's Encrypt:**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

---

## Part 5: Post-Deployment

### Step 5.1: Verify Database Connection

```bash
python manage.py check --database default
```

**Expected output:**
```
System check identified no issues (0 silenced).
```

### Step 5.2: Test Admin Login

1. Visit: `https://your-domain.com/`
2. Login with username: `admin`
3. Create a test operation
4. Create a test record
5. Test export functionality

### Step 5.3: Monitor Logs

**Render/Railway:**
- Check the dashboard logs

**Own Server:**
```bash
# Application logs
sudo journalctl -u onfield -f

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

---

## Part 6: Ongoing Maintenance

### Update Application

```bash
# Pull latest code
git pull origin main

# Activate virtual environment
source venv/bin/activate  # or .\virtualEnvironment\Scripts\activate on Windows

# Install new dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart service
sudo systemctl restart onfield  # or restart on Render/Railway
```

### Database Backups

Your Supabase database has automatic daily backups, but you can also:

```bash
# Manual backup
python manage.py dumpdata > backup_$(date +%Y%m%d).json

# Restore from backup
python manage.py loaddata backup_20251026.json
```

### Monitor Disk Usage

```bash
# Check media folder size
du -sh media/

# Check database size (in Supabase dashboard)
# Settings → Database → Usage
```

---

## Troubleshooting

### Issue: "Bad Request (400)"

**Cause**: Domain not in ALLOWED_HOSTS

**Solution**: Add your domain to `.env`:
```properties
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,your-ip
```

### Issue: "Static files not loading"

**Cause**: Static files not collected or not served

**Solution**:
```bash
python manage.py collectstatic --noinput
# Then restart your web server
```

### Issue: "Database connection failed"

**Cause**: Supabase credentials incorrect or network issue

**Solution**:
1. Check `.env` database settings
2. Test connection: `python manage.py dbshell`
3. Verify Supabase project is active

### Issue: "CSRF verification failed"

**Cause**: CSRF_COOKIE_SECURE=True but not using HTTPS

**Solution**: 
- Either setup HTTPS/SSL first
- Or set `CSRF_COOKIE_SECURE=False` (not recommended)

### Issue: "Permission denied" on media uploads

**Cause**: Web server doesn't have write access to media folder

**Solution**:
```bash
sudo chown -R onfield:onfield /var/www/onfield/OnFieldRecording/media
sudo chmod -R 755 /var/www/onfield/OnFieldRecording/media
```

---

## Security Checklist (Production)

- [ ] DEBUG=False in .env
- [ ] New SECRET_KEY generated
- [ ] ALLOWED_HOSTS set to specific domains only
- [ ] HTTPS/SSL configured
- [ ] CSRF_COOKIE_SECURE=True (after SSL)
- [ ] SESSION_COOKIE_SECURE=True (after SSL)
- [ ] SECURE_SSL_REDIRECT=True (after SSL)
- [ ] .env file not in Git repository (check .gitignore)
- [ ] Database password is strong
- [ ] Firewall configured (only ports 80, 443, 22 open)
- [ ] Regular backups scheduled
- [ ] Monitoring setup (Sentry, UptimeRobot, etc.)

---

## Performance Optimization (Optional)

### Add Redis Caching

```bash
pip install redis django-redis
```

```python
# Add to settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### Enable Database Connection Pooling

Already enabled via Supabase (port 6543) ✅

### Compress Static Files

```python
# Add to settings.py
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

---

## What Your Users Will Experience

### Staff Users
1. Visit `https://your-domain.com/`
2. Login with staff credentials
3. Automatically redirected to recording form
4. Fill in field data with GPS coordinates
5. Upload meter photos
6. Submit records

### Admin Users
1. Visit `https://your-domain.com/`
2. Login with admin credentials
3. See dashboard with all operations
4. Create/activate operations
5. Search across all records
6. Export to PDF/Excel
7. Manage users

---

## Next Steps After Deployment

1. **Test Everything**:
   - Create operation
   - Create record
   - Upload photo
   - Export to PDF/Excel
   - Search functionality
   - Dark mode toggle

2. **Train Your Team**:
   - Share login credentials
   - Walk through recording process
   - Explain operation workflow

3. **Monitor**:
   - Check Supabase database size
   - Monitor media folder growth
   - Review audit logs weekly

4. **Plan Migrations**:
   - S3 for media storage (if not done)
   - Celery for background jobs (if exports slow down)
   - Redis for caching (if dashboard gets slow)

---

## Support Resources

- **Django Deployment**: https://docs.djangoproject.com/en/5.0/howto/deployment/
- **Supabase**: https://supabase.com/docs
- **Nginx**: https://nginx.org/en/docs/
- **Let's Encrypt SSL**: https://letsencrypt.org/
- **Gunicorn**: https://docs.gunicorn.org/

---

**Deployment Date**: _______________  
**Domain**: _______________  
**Admin Username**: admin  
**Database**: Supabase PostgreSQL ✅  
**Status**: Ready for Production 🚀
