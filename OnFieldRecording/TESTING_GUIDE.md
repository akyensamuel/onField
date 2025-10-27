# Testing Guide for OnField Recording System

## Test Suite Status

### ✅ Passing Tests (13/18)
- UserProfile model tests (auto-creation via signals, roles, phone validation)
- Operation model tests (creation, string representation)
- Authentication views (login page, logout)
- Dashboard views (admin access, unauthenticated denial)
- Operation views (list, detail)
- Audit logging (log entry creation)

### ❌ Failing Tests (5/18)
**Issue**: Record model field names in tests don't match actual model

**Actual Record Model Fields:**
```python
record_number    # Not job_number
todays_balance   # Not outstanding_balance  
created_by       # Not recorded_by
```

**Fix Required**: Update test_create_record, test_record_with_gps, test_record_with_anomaly, test_first_record_number, test_sequential_record_numbers

### ⚠️ Known Issues
1. **Dashboard Access Control**: Staff users can access admin dashboard (test expects 302/403 but gets 200)
   - **Action**: Review permission decorators in views.py

2. **Test Database Cleanup**: PostgreSQL test database doesn't drop cleanly
   - **Workaround**: Manual cleanup or use `--keepdb` flag

## Running Tests

### Full Test Suite
```bash
python manage.py test DataForm.tests --verbosity=2
```

### Specific Test Class
```bash
python manage.py test DataForm.tests.UserProfileModelTest
```

### With Coverage
```bash
coverage run --source='DataForm' manage.py test DataForm.tests
coverage report
coverage html  # Generate HTML report
```

## Test Coverage Goals

### Models (60% complete)
- ✅ UserProfile: Creation, roles, permissions
- ✅ Operation: CRUD, status
- ⏳ Record: Needs field name fixes
- ⏳ RecordMedia: Not tested yet
- ✅ AuditLog: Basic creation

### Views (50% complete)
- ✅ Authentication: Login/logout
- ⏳ Dashboard: Permission issue
- ✅ Operations: List/detail
- ⏳ Records: Not tested yet

### Business Logic (30% complete)
- ⏳ Record number generation (JOB0001 sequence)
- ⏳ GPS validation
- ⏳ Anomaly detection
- ⏳ Active operation constraint

## Next Steps

1. **Fix Record Model Tests**
   - Update all Record.objects.create() calls with correct fields
   - Test record_number generation (not job_number)
   - Test todays_balance (not outstanding_balance)
   - Test created_by (not recorded_by)

2. **Fix Dashboard Permission Test**
   - Review @admin_required decorator
   - Ensure staff users are properly denied

3. **Add Missing Tests**
   - RecordMedia model tests
   - RecordMedia views
   - Export functionality
   - PDF/Excel generation

4. **Integration Tests**
   - Full workflow (create operation → add records → export)
   - File upload with Supabase Storage
   - Audit log verification

5. **Performance Tests**
   - Large dataset export (>1000 records)
   - GPS coordinate validation at scale
   - Database query optimization

## Test Database Configuration

The test suite uses PostgreSQL test database `test_postgres`. To avoid manual cleanup:

```python
# In settings.py TEST configuration
DATABASES = {
    'default': {
        ...
        'TEST': {
            'NAME': 'test_onfield_db',
        }
    }
}
```

Or use in-memory SQLite for faster tests (not recommended for production testing):

```python
import sys
if 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
```

## Continuous Integration

### GitHub Actions Workflow (Recommended)
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.13'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          python manage.py test
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
```

## Coverage Report Example

```
Name                                 Stmts   Miss  Cover
--------------------------------------------------------
DataForm/__init__.py                     0      0   100%
DataForm/models.py                     187     45    76%
DataForm/views.py                      245    123    50%
DataForm/admin.py                       42     15    64%
DataForm/signals.py                     98     62    37%
--------------------------------------------------------
TOTAL                                  572    245    57%
```

**Target**: 80% coverage before production deployment
