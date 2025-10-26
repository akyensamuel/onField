# Export Fields Update - October 26, 2025

## Overview
Updated PDF and XLSX export functionality to include only the specified fields per user requirements.

## Fields Exported (10 Total)

### 1. Job Number
- **Source**: `record.record_number`
- **Description**: Unique record identifier (e.g., OP-001-0001)
- **Format**: String

### 2. Customer Name
- **Source**: `record.customer_name`
- **Description**: Full name of the customer
- **Format**: String (max 200 characters)
- **PDF Display**: Truncated to 25 chars with ellipsis if needed

### 3. Customer Contact
- **Source**: `record.customer_contact`
- **Description**: Customer phone number
- **Format**: String (validated format: +999999999)

### 4. GPS Address
- **Source**: `record.gps_address`
- **Description**: Human-readable address from GPS coordinates
- **Format**: Text
- **PDF Display**: Truncated to 30 chars with ellipsis if needed
- **XLSX Display**: Full address (column width: 35)

### 5. Account Number
- **Source**: `record.account_number`
- **Description**: Customer account identifier
- **Format**: String (max 100 characters)

### 6. Meter Number
- **Source**: `record.meter_number`
- **Description**: Electric meter identifier
- **Format**: String (max 100 characters)

### 7. Today's Balance
- **Source**: `record.todays_balance`
- **Description**: Current account balance
- **Format**: Decimal (12 digits, 2 decimal places)
- **PDF Display**: Formatted as currency (e.g., 1,234.56)
- **XLSX Display**: Number format with 2 decimals (#,##0.00)

### 8. Meter Reading
- **Source**: `record.meter_reading`
- **Description**: Current meter reading value
- **Format**: Decimal (12 digits, 2 decimal places)
- **PDF Display**: Formatted as currency (e.g., 1,234.56)
- **XLSX Display**: Number format with 2 decimals (#,##0.00)

### 9. Type of Anomaly
- **Source**: `record.type_of_anomaly`
- **Description**: Type of issue detected
- **Format**: Choice field
- **Values**: 
  - None
  - Meter Damaged
  - Meter Missing
  - Meter Tampered
  - Incorrect Reading
  - Access Denied
  - Customer Relocated
  - Other
- **Display**: Title case with underscores replaced by spaces

### 10. Remarks
- **Source**: `record.remarks`
- **Description**: Additional notes or comments
- **Format**: Text (unlimited)
- **PDF Display**: Truncated to 20 chars with ellipsis if needed
- **XLSX Display**: Full remarks (column width: 30)

---

## PDF Export Details

### File Naming
- **Format**: `{Operation_Name}_{YYYYMMDD_HHMM}.pdf`
- **Example**: `Operation_Alpha_20251026_1430.pdf`

### Layout
- **Page Size**: Letter (8.5" x 11")
- **Orientation**: **Landscape** (11" wide x 8.5" tall)
- **Margins**: 0.5" on all sides
- **Usable Width**: ~10 inches
- **Table Structure** (10 columns optimized for landscape):
  - Column 1: Job # (0.95")
  - Column 2: Customer Name (1.35")
  - Column 3: Contact (1.0")
  - Column 4: GPS Address (1.5")
  - Column 5: Account # (0.95")
  - Column 6: Meter # (0.95")
  - Column 7: Balance (0.75")
  - Column 8: Reading (0.75")
  - Column 9: Anomaly (1.0")
  - Column 10: Remarks (0.8")

### Text Truncation (for readability)
- **Customer Name**: 30 characters (increased for landscape)
- **GPS Address**: 40 characters (increased for landscape)
- **Remarks**: 25 characters (increased for landscape)

### Styling
- **Header**: Dark gray background (#1f2937), white text, bold
- **Rows**: Alternating white and light gray (#f9fafb)
- **Font**: Helvetica, 8pt
- **Grid**: Light gray borders (#d1d5db)

---

## XLSX Export Details

### File Naming
- **Format**: `{Operation_Name}_{YYYYMMDD_HHMM}.xlsx`
- **Example**: `Operation_Alpha_20251026_1430.xlsx`

### Sheet Structure
1. **Summary Sheet**: Operation details, statistics, anomaly breakdown
2. **Records Sheet**: All record data with specified fields

### Records Sheet Layout
- **Headers**: Bold, dark gray background, white text, centered
- **Column Widths**:
  - A: Job Number (18)
  - B: Customer Name (25)
  - C: Customer Contact (18)
  - D: GPS Address (35)
  - E: Account Number (18)
  - F: Meter Number (18)
  - G: Today's Balance (15)
  - H: Meter Reading (15)
  - I: Type of Anomaly (20)
  - J: Remarks (30)

### Special Formatting
- **Currency Columns** (G, H): Number format with thousand separators and 2 decimals (#,##0.00)
- **Frozen Header**: Row 1 is frozen for easier scrolling
- **Borders**: All cells have light borders
- **Alignment**: Left-aligned text, center-aligned headers

---

## Removed Fields
The following fields were previously exported but are now **excluded** per user requirements:
- ❌ Sequential # (auto-increment)
- ❌ Status (Draft/Submitted/Verified)
- ❌ Created By (username)
- ❌ Created At (timestamp)
- ❌ Updated At (timestamp)
- ❌ GPS Latitude (decimal)
- ❌ GPS Longitude (decimal)

---

## Code Changes

### File: `DataForm/views.py`

#### PDF Export (operation_export_pdf)
- **Lines 475-515**: Updated records table headers and data rows
- **Changed**: From 6 columns to 10 columns
- **Added**: Customer contact, GPS address, meter numbers, balance, reading, remarks

#### XLSX Export (operation_export_xlsx)
- **Lines 688-748**: Updated records sheet headers and data rows
- **Changed**: From 11 columns to 10 columns
- **Added**: Customer contact, balance, reading, remarks
- **Removed**: Sequential #, Status, Created By, timestamps

---

## Testing Checklist

- [ ] PDF export with < 10 records displays correctly
- [ ] PDF export with 100+ records displays correctly
- [ ] XLSX export with < 10 records displays correctly
- [ ] XLSX export with 100+ records displays correctly
- [ ] Currency formatting works in XLSX (Balance & Reading columns)
- [ ] Long GPS addresses are truncated in PDF
- [ ] Long remarks are truncated in PDF
- [ ] Full text appears in XLSX for all fields
- [ ] Anomaly types display correctly (title case, no underscores)
- [ ] Job numbers display correctly
- [ ] Files download with correct operation name

---

## Usage

### For Admin Users
1. Navigate to operation detail page
2. Click "Export PDF" or "Export Excel" button
3. File downloads automatically with operation name

### For Data Analysis
- Use XLSX for detailed analysis with full data
- Use PDF for printing or sharing static reports
- Both formats contain identical data fields
- Summary sheet in XLSX provides operation insights

---

## Benefits

### ✅ Focused Data
- Only essential fields for field operations
- Removed system metadata (status, timestamps)
- Cleaner, more professional exports

### ✅ Better Readability
- Customer information grouped together
- Meter data grouped together
- Anomaly and remarks clearly visible

### ✅ Practical Use
- PDF fits on standard letter size (landscape)
- XLSX formatted for immediate use
- Currency values properly formatted

### ✅ Professional Output
- Files named with operation names
- Consistent formatting
- Easy to share with stakeholders

---

**Last Updated**: October 26, 2025  
**Modified By**: System Update  
**Version**: 2.0
