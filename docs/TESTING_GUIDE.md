# Testing Guide - Deletion & Export Features

## Quick Start

### Prerequisites
1. Ensure virtual environment is activated
2. All dependencies installed (reportlab, openpyxl)
3. Migrations applied
4. Django server running

### Activation Commands
```bash
cd d:\code\onField\OnFieldRecording
..\virtualEnvironment\Scripts\activate
python manage.py runserver
```

---

## Test Plan

### ✅ Test 1: Deletion Log Model

**Purpose:** Verify DeletionLog model is properly created

**Steps:**
1. Access admin panel: `http://localhost:8000/admin/`
2. Login with admin credentials
3. Look for "Deletion Logs" in the DataForm section
4. Verify the model is accessible

**Expected Result:**
- ✅ "Deletion Logs" appears in admin
- ✅ Empty list (no deletions yet)
- ✅ Cannot add new logs manually (no "Add" button)

**Status:** □ PASS □ FAIL

---

### ✅ Test 2: Operation Deletion with Audit

**Purpose:** Verify operation deletion creates audit log

**Prerequisites:**
- At least one operation exists
- Operation has some records (optional)

**Steps:**
1. Go to Operations list
2. Click on an operation to view details
3. Click "Delete" button
4. **Observe:** Modal appears
5. Try submitting without reason
   - **Expected:** Form validation prevents submission
6. Enter deletion reason (e.g., "Test deletion for audit")
7. Confirm deletion
8. Go to Admin → Deletion Logs
9. Verify entry exists

**Expected Results:**
- ✅ Modal requires deletion reason (cannot submit empty)
- ✅ Success message shows: "Operation '{name}' and its X record(s) have been deleted"
- ✅ DeletionLog entry created with:
  - `item_type` = 'operation'
  - `deleted_by` = current user
  - `deletion_reason` = entered text
  - `metadata` includes: operation_name, record_count, was_active, etc.
- ✅ Operation and all related records deleted from database
- ✅ Redirected to operation list

**Status:** □ PASS □ FAIL

**Notes:**
```
Record count deleted: _____
Deletion reason used: _____________________________
DeletionLog ID: _____
```

---

### ✅ Test 3: Record Deletion (Admin)

**Purpose:** Verify admin can delete any record

**Prerequisites:**
- At least one record exists
- Logged in as admin

**Steps:**
1. Go to Records list
2. Click on a record to view details
3. **Verify:** "Delete" button visible
4. Click "Delete" button
5. Modal appears
6. Try submitting without reason
   - **Expected:** Form validation prevents submission
7. Enter deletion reason (e.g., "Duplicate entry")
8. Confirm deletion
9. Go to Admin → Deletion Logs
10. Verify entry exists

**Expected Results:**
- ✅ Delete button visible (admin can delete any record)
- ✅ Modal requires deletion reason
- ✅ Success message: "Record {record_number} deleted successfully"
- ✅ DeletionLog entry created with:
  - `item_type` = 'record'
  - `deleted_by` = current user
  - `metadata` includes: record_number, operation, customer_name, account_number, status, anomaly, media_count
- ✅ Record and related media deleted
- ✅ Redirected to record list

**Status:** □ PASS □ FAIL

---

### ✅ Test 4: Record Deletion (Owner)

**Purpose:** Verify record creator can delete own record

**Prerequisites:**
- Record exists created by non-admin user
- Logged in as the record creator

**Steps:**
1. Go to Records list
2. Find a record you created
3. Click to view details
4. **Verify:** "Delete" button visible
5. Click "Delete" and enter reason
6. Confirm deletion

**Expected Results:**
- ✅ Delete button visible for own records
- ✅ Deletion succeeds with audit log
- ✅ Can only delete own records (not others')

**Status:** □ PASS □ FAIL

---

### ✅ Test 5: Record Deletion (Permission Denied)

**Purpose:** Verify non-admin cannot delete others' records

**Prerequisites:**
- Record exists created by another user
- Logged in as staff (not admin)

**Steps:**
1. Go to record detail page (not your record)
2. **Verify:** No "Delete" button visible OR button disabled
3. Try accessing delete URL directly: `/records/{id}/delete/`

**Expected Results:**
- ✅ Delete button not visible for others' records
- ✅ Direct URL access shows permission denied message
- ✅ Redirects back to record detail

**Status:** □ PASS □ FAIL

---

### ✅ Test 6: PDF Export

**Purpose:** Verify PDF generation works correctly

**Prerequisites:**
- At least one operation with some records
- Logged in as admin

**Steps:**
1. Go to operation detail page
2. Click "Export PDF" button (red button with PDF icon)
3. **Observe:** PDF file downloads
4. Open the PDF file
5. Verify contents:
   - Operation name and details
   - Statistics (total, draft, submitted, verified, anomalies)
   - Anomaly breakdown (if any)
   - Records table (first 100 records)
   - Generated date/time

**Expected Results:**
- ✅ PDF downloads successfully
- ✅ Filename format: `operation_{id}_YYYYMMDD.pdf`
- ✅ PDF contains all sections:
  - Title: "Operation Report"
  - Operation Details table
  - Statistics card
  - Anomaly Breakdown (if applicable)
  - Records table with data
- ✅ Professional formatting (colors, borders, fonts)
- ✅ AuditLog entry created with action_type='export', format='pdf'

**Status:** □ PASS □ FAIL

**PDF Quality Checklist:**
- □ Text is readable
- □ Tables are properly formatted
- □ No data truncation
- □ Colors render correctly
- □ All sections present

---

### ✅ Test 7: Excel Export

**Purpose:** Verify Excel generation works correctly

**Prerequisites:**
- At least one operation with records
- Logged in as admin

**Steps:**
1. Go to operation detail page
2. Click "Export Excel" button (green button with Excel icon)
3. **Observe:** XLSX file downloads
4. Open in Excel/LibreOffice
5. Verify Summary sheet:
   - Title: "Operation Report"
   - Operation Details section
   - Record Statistics section
   - Anomaly Breakdown section (if applicable)
6. Verify Records sheet:
   - All record fields as columns
   - One record per row
   - Status color coding (Draft=yellow, Submitted=blue, Verified=green)
   - Frozen header row

**Expected Results:**
- ✅ XLSX downloads successfully
- ✅ Filename format: `operation_{id}_YYYYMMDD.xlsx`
- ✅ Summary sheet exists with:
  - Merged title cells
  - Bold headers
  - Operation details table
  - Statistics summary
  - Anomaly breakdown
  - Proper formatting (colors, borders, fonts)
- ✅ Records sheet exists with:
  - Headers: #, Record Number, Customer, Account, Meter, GPS, Status, Anomaly, Created By, Created At, Updated At
  - All records listed
  - Status color coding works
  - Frozen top row
  - Proper column widths
- ✅ AuditLog entry created with action_type='export', format='xlsx'

**Status:** □ PASS □ FAIL

**Excel Quality Checklist:**
- □ Opens without errors
- □ Both sheets present
- □ Data is accurate
- □ Formulas work (if any)
- □ Color coding visible
- □ Column widths appropriate
- □ No truncated text

---

### ✅ Test 8: Large Dataset Export

**Purpose:** Verify exports handle many records gracefully

**Prerequisites:**
- Operation with 100+ records

**Steps:**
1. Export to PDF
2. Verify PDF contains note: "Showing first 100 of X records"
3. Export to Excel
4. Verify Excel contains ALL records (no limit)

**Expected Results:**
- ✅ PDF limits to 100 records with note
- ✅ Excel includes all records
- ✅ File sizes reasonable
- ✅ No timeouts or errors

**Status:** □ PASS □ FAIL

---

### ✅ Test 9: Empty Operation Export

**Purpose:** Verify exports work for operations with no records

**Prerequisites:**
- Operation with 0 records

**Steps:**
1. Export to PDF
2. Export to Excel
3. Verify both files generated

**Expected Results:**
- ✅ PDF generated with:
  - Operation details
  - Statistics showing 0s
  - No anomaly section
  - No records table
- ✅ Excel generated with:
  - Summary sheet (stats all 0)
  - Records sheet with headers only
- ✅ No errors or crashes

**Status:** □ PASS □ FAIL

---

### ✅ Test 10: Deletion Log Admin Interface

**Purpose:** Verify admin interface for viewing deletion logs

**Steps:**
1. Perform several deletions (operations and records)
2. Go to Admin → Deletion Logs
3. Test search functionality:
   - Search by item name
   - Search by deletion reason
4. Test filters:
   - Filter by item type
   - Filter by user
   - Filter by date
5. Click on a log entry
6. Verify all fields visible:
   - Deleted by user
   - Item type badge
   - Item ID and name
   - Deletion reason
   - Deleted at timestamp
   - Metadata (formatted JSON)

**Expected Results:**
- ✅ All deletions appear in list
- ✅ Search works correctly
- ✅ Filters work correctly
- ✅ Date hierarchy navigation works
- ✅ Detail view shows all information
- ✅ Metadata displayed as formatted JSON
- ✅ Item type badges color coded:
  - Operation = Blue
  - Record = Green
- ✅ Cannot add new logs manually
- ✅ Cannot edit existing logs
- ✅ Only superusers can delete logs

**Status:** □ PASS □ FAIL

---

### ✅ Test 11: Export Button Visibility

**Purpose:** Verify export buttons only visible to admins

**Prerequisites:**
- One operation exists

**Steps:**
1. Login as admin
2. Go to operation detail
3. **Verify:** "Export PDF" and "Export Excel" buttons visible
4. Logout
5. Login as staff user
6. Go to same operation detail
7. **Verify:** Export buttons hidden OR disabled

**Expected Results:**
- ✅ Admin sees both export buttons
- ✅ Staff users don't see export buttons (or see disabled buttons)
- ✅ Direct URL access blocked for non-admins

**Status:** □ PASS □ FAIL

**Note:** Current implementation may allow all users. If restriction needed, add `@admin_required` decorator verification.

---

### ✅ Test 12: Audit Log for Exports

**Purpose:** Verify exports are logged in AuditLog

**Steps:**
1. Clear recent audit logs (optional)
2. Export operation to PDF
3. Export operation to Excel
4. Go to Admin → Audit Logs
5. Filter by action_type = 'export'

**Expected Results:**
- ✅ Two export entries visible
- ✅ Entry 1: format='pdf', record_count={count}
- ✅ Entry 2: format='xlsx', record_count={count}
- ✅ IP address captured
- ✅ User captured
- ✅ Timestamp accurate

**Status:** □ PASS □ FAIL

---

### ✅ Test 13: Cascade Deletion

**Purpose:** Verify operation deletion cascades to records and media

**Prerequisites:**
- Operation with records
- Records have media files

**Steps:**
1. Note record IDs and media file names
2. Delete the operation with reason
3. Check database:
   - Records table (should be gone)
   - RecordMedia table (should be gone)
4. Check media files folder
   - Files should be deleted

**Expected Results:**
- ✅ Operation deleted
- ✅ All related records deleted
- ✅ All related media entries deleted
- ✅ Media files removed from filesystem
- ✅ Single DeletionLog entry for operation (not individual records)

**Status:** □ PASS □ FAIL

---

### ✅ Test 14: GPS Address Display in Exports

**Purpose:** Verify GPS addresses show correctly in exports

**Prerequisites:**
- Records with GPS coordinates
- Records with manual addresses

**Steps:**
1. Export operation to PDF
2. Export operation to Excel
3. Verify GPS Address column contains:
   - Lat/Lon format OR
   - Manual address text

**Expected Results:**
- ✅ GPS addresses visible in PDF
- ✅ GPS addresses visible in Excel
- ✅ Both coordinate and manual formats display
- ✅ No truncation of address data

**Status:** □ PASS □ FAIL

---

### ✅ Test 15: Dark Mode Compatibility

**Purpose:** Verify deletion modals work in dark mode

**Steps:**
1. Enable dark mode in browser/app
2. Open operation detail
3. Click "Delete" button
4. Verify modal appearance:
   - Dark background
   - Light text
   - Readable contrast
   - Proper button colors
5. Repeat for record deletion modal

**Expected Results:**
- ✅ Modals readable in dark mode
- ✅ Text has good contrast
- ✅ Buttons properly styled
- ✅ No white flash on modal open
- ✅ Consistent with app theme

**Status:** □ PASS □ FAIL

---

## Performance Tests

### Test 16: Large PDF Generation

**Scenario:** Export operation with 1000+ records to PDF

**Expected:**
- Completes in < 10 seconds
- File size < 5MB
- Browser doesn't freeze

**Status:** □ PASS □ FAIL

---

### Test 17: Large Excel Generation

**Scenario:** Export operation with 5000+ records to Excel

**Expected:**
- Completes in < 15 seconds
- File size reasonable
- All rows included
- Excel opens without lag

**Status:** □ PASS □ FAIL

---

## Security Tests

### Test 18: CSRF Protection

**Steps:**
1. Remove CSRF token from deletion form
2. Try to submit
3. Verify 403 Forbidden error

**Status:** □ PASS □ FAIL

---

### Test 19: Direct URL Access

**Steps:**
1. Logout
2. Try accessing:
   - `/operations/{id}/delete/`
   - `/records/{id}/delete/`
   - `/operations/{id}/export/pdf/`
   - `/operations/{id}/export/xlsx/`
3. Verify redirect to login

**Status:** □ PASS □ FAIL

---

### Test 20: SQL Injection Prevention

**Steps:**
1. Enter SQL injection attempts in deletion reason:
   - `'; DROP TABLE records; --`
   - `<script>alert('XSS')</script>`
2. Submit deletion
3. Check deletion log
4. Verify data escaped/sanitized

**Status:** □ PASS □ FAIL

---

## Bug Reports

### Bug Template
```
**Bug ID:** BUG-XXX
**Test:** Test #X
**Severity:** Critical / High / Medium / Low
**Description:** 
What happened:

What should happen:

**Steps to Reproduce:**
1.
2.
3.

**Environment:**
- Browser:
- OS:
- Python version:
- Django version:

**Screenshots/Logs:**
```

---

## Test Summary

**Total Tests:** 20
**Passed:** ___
**Failed:** ___
**Skipped:** ___

**Pass Rate:** ___%

**Critical Issues:** ___
**Major Issues:** ___
**Minor Issues:** ___

**Tested By:** _______________
**Date:** _______________
**Environment:** Development / Staging / Production

---

## Sign-Off

### Developer
- Name: _______________
- Date: _______________
- Signature: _______________

### QA Lead
- Name: _______________
- Date: _______________
- Signature: _______________

### Product Owner
- Name: _______________
- Date: _______________
- Signature: _______________

---

## Notes

**Known Issues:**
1. 

**Deferred Tests:**
1.

**Additional Testing Needed:**
1.

