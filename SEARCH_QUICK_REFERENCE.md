# Search Functionality Quick Reference

## 🔍 Two Search Modes (Admin Only)

### 1️⃣ Operation-Wide Search
**Access**: Operation Detail Page → "Search Records" button (purple)  
**URL**: `/operations/<id>/search/`  
**Searches**: Records within ONE specific operation  

### 2️⃣ System-Wide Search
**Access**: Admin Dashboard → Prominent gradient search bar  
**URL**: `/search/`  
**Searches**: ALL records across ALL operations  

---

## 📋 Searchable Fields (7-8 fields)

| Field | Operation Search | System Search |
|-------|-----------------|---------------|
| Customer Name | ✅ | ✅ |
| Customer Contact | ✅ | ✅ |
| Account Number | ✅ | ✅ |
| Meter Number | ✅ | ✅ |
| GPS Address | ✅ | ✅ |
| Job Number | ✅ | ✅ |
| Remarks | ✅ | ✅ |
| **Operation Name** | ❌ | ✅ |

---

## 🎯 Quick Usage

### Operation-Wide Search
```
1. Go to Operations → Select Operation
2. Click "Search Records" (purple button)
3. Enter search term
4. View filtered results
```

### System-Wide Search
```
1. Go to Admin Dashboard
2. Use search bar at top (blue-purple gradient)
3. Enter search term
4. View results from all operations
```

---

## 💡 Search Examples

| What You Want | Search For |
|---------------|------------|
| Find customer "Juan Dela Cruz" | `Juan` or `Dela Cruz` |
| Find phone number 09123456789 | `0912` or `09123456789` |
| Find account ACC-001-123 | `ACC-001` or `123` |
| Find records with broken meters | `broken` |
| Find job OP-001-0001 | `OP-001` |
| Find Quezon City addresses | `Quezon` |

---

## 📊 Results Display

**Operation Search Shows:**
- Job #, Customer, Contact, Account #, Meter #, Balance, Reading, Anomaly, Actions

**System Search Shows:**
- Job #, **Operation**, Customer, Contact, Account #, Meter #, Balance, Reading, Anomaly, Actions

---

## ⚡ Features

✅ **Partial Matching**: Search "Juan" finds "Juan Dela Cruz"  
✅ **Case Insensitive**: "JUAN", "juan", "Juan" all work  
✅ **Multi-Field**: Searches ALL fields at once  
✅ **Pagination**: 50 results per page  
✅ **Dark Mode**: Full support  
✅ **Mobile Friendly**: Responsive design  

---

## 🔒 Security

- **Admin Only**: Requires admin role
- **Non-admins**: Redirected with error message
- **SQL Safe**: Protected by Django ORM
- **CSRF Protected**: All form submissions

---

## 🎨 UI Locations

### Operation Detail Page
```
[Operation Header]
[Search Records] [Export PDF] [Export Excel] [Close/Activate] [Delete]
```

### Admin Dashboard
```
[Admin Dashboard]
┌─────────────────────────────────────────┐
│ 🔍 Search All Records                   │
│ [Large Search Input Field] [Search]     │
│ Search across all operations...         │
└─────────────────────────────────────────┘
[Active Operation Status]
[Stats Cards]
```

---

## 📱 User Flow

```
Admin Dashboard
    ↓
Search Bar (System-Wide)
    ↓
Enter Query → Submit
    ↓
Search Results Page
    ├─ Table with Results
    ├─ Pagination (if >50)
    └─ View Record Details
```

```
Operation Detail
    ↓
"Search Records" Button
    ↓
Operation Search Page
    ↓
Enter Query → Submit
    ↓
Filtered Results (Operation Only)
    ├─ Table with Results
    ├─ Pagination (if >50)
    └─ View Record Details
```

---

**Created**: October 26, 2025  
**Access**: Admin Users Only  
**Status**: ✅ Production Ready
