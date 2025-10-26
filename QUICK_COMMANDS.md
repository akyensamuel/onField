# Quick Production Commands
**OnField Recording System - Command Reference**

---

## 🔥 Most Common Commands

### Generate New SECRET_KEY
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Collect Static Files
```bash
cd OnFieldRecording
python manage.py collectstatic --noinput
```

### Run Database Migrations
```bash
python manage.py migrate
```

### Create Superuser
```bash
python manage.py createsuperuser --username admin --email admin@yoursite.com
```

### Check for Issues
```bash
python manage.py check
python manage.py check --database default
python manage.py check --deploy  # Production-specific checks
```

### Backup Database
```bash
python manage.py dumpdata > backup_$(date +%Y%m%d_%H%M%S).json
```

### Restore Database
```bash
python manage.py loaddata backup_20251026_143000.json
```

### Run Development Server
```bash
python manage.py runserver
```

### Run Production Server (Gunicorn)
```bash
gunicorn --workers 3 --bind 0.0.0.0:8000 OnFieldRecording.wsgi:application
```

---

## 📦 Package Management

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Update requirements.txt
```bash
pip freeze > requirements.txt
```

### Install Gunicorn (Production)
```bash
pip install gunicorn
```

---

## 🔐 Security

### Test HTTPS Configuration
```bash
python manage.py check --deploy
```

### Change User Password (Django Admin)
```bash
python manage.py changepassword admin
```

---

## 📊 Database

### Open Database Shell
```bash
python manage.py dbshell
```

### Show Migrations
```bash
python manage.py showmigrations
```

### Create New Migration
```bash
python manage.py makemigrations
```

### Fake Migration (if already applied manually)
```bash
python manage.py migrate --fake
```

---

## 🧹 Cleanup

### Clear Sessions
```bash
python manage.py clearsessions
```

### Clear Cache (if Redis configured)
```bash
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()
```

---

## 📝 Logs & Monitoring

### View Application Logs (systemd)
```bash
sudo journalctl -u onfield -f
```

### View Nginx Logs
```bash
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Restart Services
```bash
# Application
sudo systemctl restart onfield

# Nginx
sudo systemctl restart nginx
```

---

## 🐛 Debugging

### Django Shell
```bash
python manage.py shell
```

### Test Database Connection
```python
python manage.py shell
>>> from django.db import connection
>>> connection.ensure_connection()
>>> print("Database connected!")
```

### Check Installed Apps
```python
python manage.py shell
>>> from django.conf import settings
>>> print(settings.INSTALLED_APPS)
```

---

## 🚀 Deployment

### Full Deployment (after git pull)
```bash
# 1. Pull latest code
git pull origin main

# 2. Activate virtual environment
source venv/bin/activate  # Linux/Mac
# OR
.\virtualEnvironment\Scripts\activate  # Windows

# 3. Install new packages
pip install -r requirements.txt

# 4. Run migrations
cd OnFieldRecording
python manage.py migrate

# 5. Collect static files
python manage.py collectstatic --noinput

# 6. Restart application
sudo systemctl restart onfield  # Linux with systemd
# OR restart via Render/Railway dashboard
```

---

## 💾 Backup & Restore

### Full Backup
```bash
# Database
python manage.py dumpdata > backup_full.json

# Media files (Linux/Mac)
tar -czf media_backup.tar.gz media/

# Media files (Windows)
tar -czf media_backup.tar.gz media\
```

### Restore
```bash
# Database
python manage.py loaddata backup_full.json

# Media files
tar -xzf media_backup.tar.gz
```

---

## 🔍 Testing

### Run Tests (when you add them)
```bash
python manage.py test
python manage.py test DataForm  # Test specific app
```

### Coverage Report (when you add tests)
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

---

## 🌐 Git Commands

### Initialize Repository
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/akyensamuel/onField.git
git push -u origin main
```

### Update Repository
```bash
git add .
git commit -m "Your commit message"
git push origin main
```

### Pull Latest Changes
```bash
git pull origin main
```

---

## 📱 Common Workflows

### Add New Feature
```bash
# 1. Create feature branch
git checkout -b feature/new-feature

# 2. Make changes
# ... edit code ...

# 3. Test locally
python manage.py runserver

# 4. Commit changes
git add .
git commit -m "Add new feature"

# 5. Push and create PR
git push origin feature/new-feature

# 6. After merge, deploy
git checkout main
git pull origin main
# ... run deployment steps ...
```

### Update Production
```bash
# On production server
cd /var/www/onfield
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
cd OnFieldRecording
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart onfield
```

---

## 🎯 Quick Fixes

### "Bad Request (400)"
```bash
# Check ALLOWED_HOSTS in .env
nano .env
# Add: ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

### "Static files not loading"
```bash
python manage.py collectstatic --noinput
sudo systemctl restart onfield
```

### "Database connection error"
```bash
# Test connection
python manage.py check --database default

# Check Supabase status
# Visit: https://status.supabase.com/
```

### "Permission denied" errors
```bash
# Fix ownership (Linux)
sudo chown -R onfield:onfield /var/www/onfield
sudo chmod -R 755 /var/www/onfield
```

---

## 📞 Emergency Commands

### Restart Everything (Linux)
```bash
sudo systemctl restart onfield
sudo systemctl restart nginx
```

### Reset Admin Password
```bash
python manage.py changepassword admin
```

### Emergency Database Restore
```bash
# Stop application
sudo systemctl stop onfield

# Restore backup
python manage.py loaddata emergency_backup.json

# Start application
sudo systemctl start onfield
```

---

**Keep this file handy!** 📌
