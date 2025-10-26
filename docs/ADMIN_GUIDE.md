# OnField Recording System - Admin Guide

## Quick Start

### Accessing the Admin Panel

1. **URL**: http://127.0.0.1:8000/admin/
2. **Username**: `admin`
3. **Password**: (the password you just set)

---

## Admin Panel Features

### 1. User Management

**Location**: Authentication and Authorization > Users

**Features**:
- View all users with their roles (Staff/Admin)
- Create new users
- Edit user profiles inline
- Set permissions and groups
- User profile includes:
  - Role (Staff or Admin)
  - Employee ID
  - Phone Number

**To Create a New User**:
1. Go to Users > Add User
2. Enter username and password
3. Click Save and Continue
4. In the Profile section, set:
   - Role: Staff or Admin
   - Employee ID (optional)
   - Phone Number (optional)
5. Set permissions:
   - **Staff members**: No need for "Staff status" checkbox
   - **Admins**: Check "Staff status" to access admin panel
6. Click Save

---

### 2. Operations Management

**Location**: DataForm > Operations

**Features**:
- Create new field operations/campaigns
- View operation status (Active/Closed/Deleted)
- See total records per operation
- View operation duration
- Activate/Close operations
- View all records within an operation

**Operation Workflow**:

1. **Create Operation**:
   - Name (unique, required)
   - Description (optional)
   - Status: Check "Is active" to make it the current operation
   - **Note**: Only ONE operation can be active at a time

2. **Active Operation**:
   - Staff can only create records in the active operation
   - Shows green "ACTIVE" badge
   - Auto-tracks start time

3. **Close Operation**:
   - Select operation
   - From Actions dropdown: "Close selected operations"
   - Automatically sets end time and closed_by user
   - Records become read-only for staff (admins can still edit)

4. **Reopen Operation**:
   - Select closed operation
   - From Actions dropdown: "Activate selected operations"
   - Becomes active again (only if no other operation is active)

---

### 3. Records Management

**Location**: DataForm > Records

**Features**:
- View all field records
- Filter by: Status, Anomaly Type, Operation, Date
- Search by: Record Number, Customer Name, Contact, Account Number, Meter Number
- Visual indicators:
  - 📍 Green pin: Has GPS coordinates
  - Status badges: Draft (gray), Submitted (blue), Verified (green)
  - Anomaly badges: Orange if anomaly detected

**Record Fields** (9 Core Fields):
1. Customer Name
2. Customer Contact (phone validation)
3. GPS Latitude
4. GPS Longitude
5. GPS Address (human-readable)
6. Account Number
7. Meter Number
8. Today's Balance (currency)
9. Meter Reading (numeric)

**Additional Fields**:
- Type of Anomaly (dropdown)
- Remarks (text)
- Status (Draft/Submitted/Verified)
- Photos (attached via Record Media)

**Record Number Format**: `JOB-{operation_id:03d}-{sequence:04d}`
- Example: `JOB-001-0042` (Operation 1, 42nd record)
- Auto-generated, cannot be edited

---

### 4. Record Media (Photos)

**Location**: DataForm > Record media files

**Features**:
- Upload photos for records
- View thumbnails in list
- Preview images
- Track file size
- OCR processing status (for future use)

**Photo Requirements**:
- Max size: 5 MB
- Formats: JPG, JPEG, PNG
- Multiple photos per record allowed

**To Add Photos to a Record**:
1. Edit a record
2. Scroll to "Record Media Files" section at bottom
3. Click "Add another Record Media"
4. Upload image
5. Save

---

### 5. Audit Log

**Location**: DataForm > Audit logs

**Features**:
- View all system changes (immutable log)
- Track who did what and when
- See IP addresses
- View detailed change information in JSON format

**Logged Actions**:
- Record creation/updates/deletion
- Operation creation/closing/reopening
- Media uploads
- User login/logout
- Password changes
- Data exports

**Note**: Audit logs cannot be created or deleted manually - they're auto-generated.

---

### 6. User Profiles

**Location**: DataForm > User Profiles

**Alternative View**: Shows user profiles separately (same data as User inline)

**Use Case**: Quick view of all staff roles and contact information

---

## Important Rules & Constraints

### Operation Rules:
- ✅ Only ONE operation can be active at a time
- ✅ Cannot delete operation if it has records
- ✅ Soft-delete available (sets is_deleted flag)

### Record Rules:
- ✅ Can only create records in ACTIVE operations
- ✅ GPS coordinates must be both present or both absent
- ✅ Record numbers are auto-generated (JOB-XXX-YYYY)
- ✅ Phone numbers must be valid format

### User Rules:
- ✅ UserProfile automatically created when User is created
- ✅ Use Django's built-in Groups for additional permissions
- ✅ Staff role vs Admin role is separate from Django "Staff status"

---

## Common Tasks

### Task 1: Set Up a New Field Operation

1. Go to Operations > Add Operation
2. Enter name: "November 2025 Field Survey"
3. Enter description (optional)
4. Check "Is active" (will auto-close any other active operation)
5. Click Save
6. Operation is now ready for staff to create records

### Task 2: Create a Staff User

1. Go to Users > Add User
2. Username: `staff1`, Password: (set secure password)
3. Save and Continue
4. In Profile section:
   - Role: Staff
   - Employee ID: EMP001
   - Phone: +1234567890
5. **Important**: Do NOT check "Staff status" (staff don't need admin access)
6. Save

### Task 3: Create an Admin User

1. Go to Users > Add User
2. Username: `manager1`, Password: (set secure password)
3. Save and Continue
4. In Profile section:
   - Role: Admin
   - Employee ID: MGR001
5. **Important**: CHECK "Staff status" (admins need admin panel access)
6. Save

### Task 4: Review Field Data

1. Go to Records
2. Use filters:
   - Operation: Select current operation
   - Status: Submitted
3. Click on any record to see details
4. Review GPS coordinates, meter readings, photos
5. Change status to "Verified" if correct
6. Save

### Task 5: Close an Operation

1. Go to Operations
2. Select the active operation (checkbox)
3. Actions dropdown: "Close selected operations"
4. Click Go
5. Operation status changes to CLOSED
6. End time is recorded automatically

---

## Next Steps

After familiarizing yourself with the admin panel, you'll have:

1. ✅ **Front-end Staff Interface** - Mobile-optimized form for field data entry
2. ✅ **Dashboard** - Visual stats and charts for operations
3. ✅ **Export to Excel** - Generate XLSX reports with insights
4. ✅ **GPS Integration** - One-click GPS capture from mobile devices
5. ✅ **Photo Upload** - Direct camera capture and upload

---

## Tips & Best Practices

1. **Create test data first**: Use the admin to create a test operation and a few records
2. **Test user permissions**: Create both staff and admin users to test access levels
3. **Use the search**: All admin views have powerful search and filter
4. **Check audit logs**: Review what changes are being tracked
5. **Test record numbering**: Create multiple records to see auto-incrementing numbers
6. **Upload test photos**: Test the 5MB limit and file type validation

---

## Troubleshooting

### Issue: Can't activate operation
- **Cause**: Another operation is already active
- **Solution**: Close the other operation first, then activate

### Issue: Can't create records
- **Cause**: No active operation
- **Solution**: Activate an operation first

### Issue: User can't login to admin
- **Cause**: "Staff status" not checked
- **Solution**: Edit user, check "Staff status", save

### Issue: Photo upload fails
- **Cause**: File too large or wrong format
- **Solution**: Ensure file is < 5MB and is JPG/PNG

---

## Database Location

- **Development DB**: `d:\code\onField\OnFieldRecording\db.sqlite3`
- **Media Files**: `d:\code\onField\OnFieldRecording\media\records\`

**Backup Recommendation**: Regularly backup the `db.sqlite3` file and `media` folder.

---

## Server Commands

**Start Server**:
```bash
D:/code/onField/virtualEnvironment/Scripts/python.exe D:/code/onField/OnFieldRecording/manage.py runserver
```

**Create Superuser**:
```bash
D:/code/onField/virtualEnvironment/Scripts/python.exe D:/code/onField/OnFieldRecording/manage.py createsuperuser
```

**Make Migrations** (after model changes):
```bash
D:/code/onField/virtualEnvironment/Scripts/python.exe D:/code/onField/OnFieldRecording/manage.py makemigrations
D:/code/onField/virtualEnvironment/Scripts/python.exe D:/code/onField/OnFieldRecording/manage.py migrate
```

---

## Support

For issues or questions, check:
1. Django admin documentation: https://docs.djangoproject.com/en/5.2/ref/contrib/admin/
2. Audit logs for recent changes
3. Server console for error messages
