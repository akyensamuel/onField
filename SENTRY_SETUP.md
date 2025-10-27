# Sentry Error Monitoring Setup Guide
**OnField Recording System - Production Error Tracking**  
**Date**: October 26, 2025

---

## 🎯 Overview

Sentry provides real-time error tracking and monitoring for your Django application. Get instant alerts when errors occur in production.

---

## Why Sentry?

### Benefits
✅ **Real-Time Alerts**: Instant notifications when errors occur  
✅ **Stack Traces**: See exactly where errors happened  
✅ **User Context**: Know which user encountered the error  
✅ **Performance Monitoring**: Track slow database queries  
✅ **Release Tracking**: See which deployment introduced bugs  
✅ **Free Tier**: 5,000 errors/month included  

### What You'll Monitor
- Python exceptions
- Django template errors
- Database query errors
- 404/500 errors
- Slow page loads
- Failed file uploads

---

## Step 1: Create Sentry Account

### 1.1 Sign Up

1. Go to https://sentry.io/
2. Click "Get Started"
3. Sign up with GitHub (recommended) or email
4. Choose **Free** plan (5K errors/month)

### 1.2 Create Project

1. Click "Create Project"
2. **Platform**: Select **Django**
3. **Alert frequency**: Choose "On every new issue"
4. **Project name**: `onfield-recording`
5. Click "Create Project"

### 1.3 Get DSN

After creating the project:
1. You'll see setup instructions
2. Copy the **DSN** (looks like: `https://abc123@o456.ingest.sentry.io/789`)
3. Keep this handy

---

## Step 2: Configure Your Application

### 2.1 Update `.env` File

Add this line to `d:\code\onField\.env`:

```properties
# Sentry Error Monitoring
SENTRY_DSN=https://your-actual-dsn@o123456.ingest.sentry.io/7891011
SENTRY_ENVIRONMENT=production
```

**Replace** `SENTRY_DSN` with the actual DSN from Step 1.3

### 2.2 For Render.com

Add environment variables in Render dashboard:

1. Go to https://dashboard.render.com/
2. Select your service
3. Click **Environment** tab
4. Add:
   - `SENTRY_DSN=https://your-dsn@sentry.io/123`
   - `SENTRY_ENVIRONMENT=production`
5. Click "Save Changes"

### 2.3 For Development

In your local `.env`:
```properties
SENTRY_DSN=  # Leave empty or use different DSN for dev
SENTRY_ENVIRONMENT=development
```

---

## Step 3: Verify Installation

### 3.1 Check Settings

The Sentry configuration is already in `settings.py`:

```python
# Sentry Error Monitoring
SENTRY_DSN = config('SENTRY_DSN', default='')
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,  # 10% of transactions
        send_default_pii=False,  # Don't send personally identifiable information
        environment=config('SENTRY_ENVIRONMENT', default='production'),
    )
```

✅ **Already configured!**

### 3.2 Install Package

```bash
pip install sentry-sdk
```

This is already in `requirements.txt`, so it installs automatically on deployment.

---

## Step 4: Test Error Reporting

### 4.1 Create Test View (Temporary)

Add to `DataForm/views.py` (for testing only):

```python
def sentry_debug(request):
    """Test view to trigger Sentry error (remove after testing)"""
    division_by_zero = 1 / 0
```

Add to `DataForm/urls.py`:

```python
path('sentry-debug/', views.sentry_debug),
```

### 4.2 Trigger Test Error

1. Deploy your application (or run locally)
2. Visit: `https://your-domain.com/sentry-debug/`
3. You should see a 500 error

### 4.3 Check Sentry Dashboard

1. Go to https://sentry.io/
2. Click on your `onfield-recording` project
3. You should see the error appear within seconds!
4. Click on it to see:
   - Stack trace
   - Request data
   - User info (if logged in)
   - Browser/OS details

### 4.4 Remove Test Code

After verifying Sentry works, **remove** the test view from your code.

---

## Step 5: Configure Alerts

### 5.1 Email Notifications

1. In Sentry Dashboard → **Settings** → **Alerts**
2. **Default alert rule**: "Send notification on every new issue"
3. Add your email address
4. Save

### 5.2 Slack Integration (Optional)

1. In Sentry Dashboard → **Settings** → **Integrations**
2. Find **Slack**
3. Click "Install"
4. Choose your Slack workspace
5. Select channel for alerts (e.g., `#errors`)
6. Test it!

### 5.3 Custom Alert Rules

Create rules like:
- Alert when error occurs > 10 times in 1 hour
- Alert on high priority errors only
- Alert when new error type appears

---

## What Gets Reported to Sentry

### ✅ Automatically Captured

- **Python Exceptions**: All unhandled errors
- **Django Template Errors**: Variable not found, etc.
- **Database Errors**: Connection failures, query errors
- **500 Errors**: Internal server errors
- **Request Context**: URL, method, headers (no PII)
- **User Context**: Username (if logged in)
- **Environment**: Python version, Django version, packages

### ❌ Not Captured (Privacy)

- Passwords
- Customer contact info
- GPS coordinates
- File contents
- Session data (unless explicitly enabled)

**Note**: We set `send_default_pii=False` to protect user privacy.

---

## Understanding Sentry Dashboard

### Key Sections

#### 1. **Issues**
- List of all errors
- Grouped by type
- Shows frequency and users affected

#### 2. **Performance**
- Slow database queries
- Page load times
- API response times

#### 3. **Releases**
- Track which deployment introduced errors
- Compare error rates between releases

#### 4. **Users**
- See which users hit errors most
- Identify problematic accounts

---

## Common Errors You'll See

### Example 1: File Upload Error
```
FileNotFoundError: [Errno 2] No such file or directory: '/media/...'
```
**Action**: Check media storage configuration

### Example 2: Database Connection
```
psycopg2.OperationalError: could not connect to server
```
**Action**: Verify Supabase credentials

### Example 3: Template Error
```
TemplateDoesNotExist at /dashboard/
```
**Action**: Check template path

### Example 4: Permission Error
```
PermissionDenied: User does not have admin role
```
**Action**: Check user permissions (expected behavior)

---

## Best Practices

### ✅ Do's

1. **Monitor Daily**: Check Sentry dashboard once per day
2. **Fix High Priority**: Address errors affecting many users first
3. **Add Context**: Use Sentry tags for better filtering
4. **Set Up Alerts**: Get notified immediately for critical errors
5. **Track Releases**: Tag deployments to identify when bugs appeared

### ❌ Don'ts

1. **Don't Ignore Errors**: Even small errors can accumulate
2. **Don't Log Everything**: Filter out expected errors (404s)
3. **Don't Expose PII**: Keep `send_default_pii=False`
4. **Don't Delay Fixes**: Address errors promptly
5. **Don't Disable in Production**: Always keep Sentry enabled

---

## Custom Error Tagging

### Add Context to Errors

```python
# In your views
import sentry_sdk

def record_create(request):
    try:
        # Your code
        record.save()
    except Exception as e:
        # Add context before error propagates
        sentry_sdk.set_context("record", {
            "job_number": record.job_number,
            "operation": str(record.operation),
        })
        sentry_sdk.set_tag("error_type", "record_creation")
        raise  # Re-raise to let Sentry catch it
```

### User Identification

```python
# Already configured in settings
sentry_sdk.set_user({
    "id": request.user.id,
    "username": request.user.username,
    "email": request.user.email,
})
```

---

## Filtering Noise

### Ignore Expected Errors

```python
# settings.py
sentry_sdk.init(
    # ... other settings ...
    ignore_errors=[
        'Http404',  # Don't track 404 errors
        'PermissionDenied',  # Don't track auth errors
    ],
)
```

### Before Send Hook

```python
# settings.py
def before_send(event, hint):
    # Modify event before sending
    if 'exc_info' in hint:
        exc_type, exc_value, tb = hint['exc_info']
        if isinstance(exc_value, Http404):
            return None  # Don't send
    return event

sentry_sdk.init(
    # ... other settings ...
    before_send=before_send,
)
```

---

## Performance Monitoring

### Enable Transaction Tracking

Already enabled with `traces_sample_rate=0.1` (10% of requests):

```python
sentry_sdk.init(
    traces_sample_rate=0.1,  # 10% sampling
)
```

### View Performance Data

1. Go to Sentry Dashboard → **Performance**
2. See:
   - Slowest endpoints
   - Database query times
   - External API calls
   - Memory usage

### Optimize Slow Queries

If you see slow operations:
1. Add database indexes
2. Use `select_related()` / `prefetch_related()`
3. Cache frequently accessed data

---

## Cost & Limits

### Free Tier
- **Errors**: 5,000/month
- **Performance**: 10,000 transactions/month
- **Retention**: 30 days
- **Team members**: Unlimited

### If You Exceed Free Tier

**Upgrade to Developer Plan** ($26/month):
- 50,000 errors/month
- 100,000 transactions/month
- 90 days retention

**Or optimize**:
- Reduce `traces_sample_rate` to 0.05 (5%)
- Filter out noisy errors
- Fix errors to reduce volume

---

## Troubleshooting

### Issue: "No errors appearing in Sentry"

**Causes**:
1. `SENTRY_DSN` not set
2. Invalid DSN
3. No errors occurred yet

**Fix**:
1. Check `.env` has correct DSN
2. Use test view to trigger error
3. Check Sentry project is active

### Issue: "Too many errors"

**Cause**: Same error repeating  
**Fix**:
1. Click "Resolve" on the issue
2. Fix the underlying code
3. Deploy fix
4. Monitor for recurrence

### Issue: "Can't see user info"

**Cause**: User not logged in or not set  
**Fix**: User context is automatically set for authenticated users

---

## Security Considerations

### What's Safe to Send

✅ Error messages
✅ Stack traces
✅ Request URLs (without sensitive query params)
✅ User IDs (not emails/passwords)
✅ Browser/OS info

### What to Protect

❌ Passwords
❌ Customer PII (names, contacts, addresses)
❌ GPS coordinates
❌ Session tokens
❌ API keys

**Our config already protects these with `send_default_pii=False`**

---

## Integration with Other Tools

### GitHub Issues

1. Sentry Dashboard → **Settings** → **Integrations** → **GitHub**
2. Connect your `onField` repository
3. Create GitHub issues directly from Sentry errors

### Discord/Telegram

Similar to Slack:
1. Find integration in Sentry
2. Connect your server/channel
3. Get notifications

---

## Summary

### What You've Accomplished

✅ Real-time error monitoring (Sentry)  
✅ Automatic error reporting  
✅ Stack traces and context  
✅ User-friendly dashboard  
✅ Email/Slack alerts  
✅ Privacy-safe configuration  

### Next Steps

1. Create Sentry account (5 min)
2. Get DSN
3. Add to `.env` and Render
4. Test with debug view
5. Configure alerts
6. Remove debug view
7. Monitor production!

**Total Setup Time**: ~15 minutes

---

**Status**: Production Monitoring Ready 🚀  
**Complexity**: Low  
**Impact**: High (catch errors before users report them!)
