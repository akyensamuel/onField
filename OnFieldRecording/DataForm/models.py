from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
import os


# =============================================
# USER PROFILE MODEL
# =============================================

class UserProfile(models.Model):
    """Extended user profile with role and additional fields"""
    
    ROLE_CHOICES = [
        ('staff', 'Staff'),
        ('admin', 'Admin'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='staff')
    employee_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_staff_member(self):
        return self.role == 'staff'


# =============================================
# OPERATION MODEL
# =============================================

class Operation(models.Model):
    """Campaign/Operation for organizing field records"""
    
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='operations_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False, db_index=True)
    start_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)
    next_record_seq = models.IntegerField(default=1, help_text="Next sequence number for record numbering")
    is_deleted = models.BooleanField(default=False)
    closed_at = models.DateTimeField(null=True, blank=True)
    closed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='operations_closed')
    
    class Meta:
        verbose_name = 'Operation'
        verbose_name_plural = 'Operations'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active', '-created_at']),
            models.Index(fields=['is_deleted']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(is_active=False) | models.Q(is_deleted=False),
                name='no_active_deleted_operation'
            )
        ]
    
    def __str__(self):
        status = "ACTIVE" if self.is_active else "CLOSED"
        return f"{self.name} ({status})"
    
    def save(self, *args, **kwargs):
        # Validate only one active operation at a time
        if self.is_active and not self.is_deleted:
            active_ops = Operation.objects.filter(is_active=True, is_deleted=False).exclude(pk=self.pk)
            if active_ops.exists():
                raise ValidationError("Only one operation can be active at a time.")
        
        # Set start_at when first activated
        if self.is_active and not self.start_at:
            self.start_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    def close_operation(self, user):
        """Close the operation"""
        self.is_active = False
        self.end_at = timezone.now()
        self.closed_at = timezone.now()
        self.closed_by = user
        self.save()
    
    def reopen_operation(self):
        """Reopen a closed operation"""
        self.is_active = True
        self.end_at = None
        self.closed_at = None
        self.closed_by = None
        self.save()
    
    @property
    def total_records(self):
        """Get total number of records for this operation"""
        return self.records.filter(is_deleted=False).count()
    
    @property
    def duration_days(self):
        """Calculate operation duration in days"""
        if self.start_at:
            end = self.end_at or timezone.now()
            return (end - self.start_at).days
        return 0


# =============================================
# RECORD MODEL
# =============================================

class Record(models.Model):
    """On-field data entry record"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('verified', 'Verified'),
    ]
    
    ANOMALY_CHOICES = [
        ('none', 'No Anomaly'),
        ('meter_damaged', 'Meter Damaged'),
        ('meter_missing', 'Meter Missing'),
        ('meter_tampered', 'Meter Tampered'),
        ('incorrect_reading', 'Incorrect Reading'),
        ('access_denied', 'Access Denied'),
        ('customer_relocated', 'Customer Relocated'),
        ('other', 'Other'),
    ]
    
    # Core fields
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE, related_name='records')
    record_number = models.CharField(max_length=50, unique=True, db_index=True, editable=False)
    
    # Customer information (9 required fields from spec)
    customer_name = models.CharField(max_length=200)
    customer_contact = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Contact must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )
    
    # GPS information
    gps_latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        null=True,
        blank=True
    )
    gps_longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        null=True,
        blank=True
    )
    gps_address = models.TextField(blank=True, help_text="Human-readable address from GPS")
    
    # Meter information
    account_number = models.CharField(max_length=100, db_index=True)
    meter_number = models.CharField(max_length=100, db_index=True)
    todays_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    meter_reading = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    # Anomaly and notes
    type_of_anomaly = models.CharField(max_length=50, choices=ANOMALY_CHOICES, default='none')
    remarks = models.TextField(blank=True)
    
    # Metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='records_created')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Record'
        verbose_name_plural = 'Records'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['operation', '-created_at']),
            models.Index(fields=['record_number']),
            models.Index(fields=['account_number']),
            models.Index(fields=['meter_number']),
            models.Index(fields=['status']),
            models.Index(fields=['type_of_anomaly']),
        ]
    
    def __str__(self):
        return f"{self.record_number} - {self.customer_name}"
    
    def clean(self):
        """Custom validation"""
        # Ensure GPS coordinates are both present or both absent
        if (self.gps_latitude is None) != (self.gps_longitude is None):
            raise ValidationError("Both latitude and longitude must be provided together.")
        
        # Validate that operation is active when creating (only check if operation_id is set)
        # Use operation_id to avoid RelatedObjectDoesNotExist error during form validation
        if not self.pk and self.operation_id:
            try:
                operation = Operation.objects.get(pk=self.operation_id)
                if not operation.is_active:
                    raise ValidationError("Cannot create records for inactive operations.")
            except Operation.DoesNotExist:
                pass  # Let the foreign key handle this validation
    
    @property
    def has_gps(self):
        """Check if record has GPS coordinates"""
        return self.gps_latitude is not None and self.gps_longitude is not None
    
    @property
    def has_anomaly(self):
        """Check if record has any anomaly"""
        return self.type_of_anomaly != 'none'


# =============================================
# RECORD MEDIA MODEL
# =============================================

def record_media_upload_path(instance, filename):
    """Generate upload path for record media"""
    ext = filename.split('.')[-1]
    operation_id = instance.record.operation.id
    record_number = instance.record.record_number
    filename = f"{timezone.now().strftime('%Y%m%d_%H%M%S')}_{instance.record.id}.{ext}"
    return f'records/operation_{operation_id}/{record_number}/{filename}'


class RecordMedia(models.Model):
    """Media files (photos) attached to records"""
    
    record = models.ForeignKey(Record, on_delete=models.CASCADE, related_name='media_files')
    image = models.ImageField(upload_to=record_media_upload_path)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_size = models.IntegerField(help_text="File size in bytes", editable=False)
    is_processed = models.BooleanField(default=False, help_text="Whether OCR/image processing has been done")
    ocr_result = models.TextField(blank=True, help_text="OCR extracted text")
    ocr_confidence = models.FloatField(null=True, blank=True, help_text="OCR confidence score")
    
    class Meta:
        verbose_name = 'Record Media'
        verbose_name_plural = 'Record Media Files'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"Media for {self.record.record_number}"
    
    def save(self, *args, **kwargs):
        """Calculate file size before saving"""
        if self.image and hasattr(self.image, 'size'):
            self.file_size = self.image.size
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validate file size and type"""
        if self.image:
            # Check file size (5MB max)
            max_size = 5 * 1024 * 1024  # 5MB in bytes
            if hasattr(self.image, 'size') and self.image.size > max_size:
                raise ValidationError(f"Image file too large ( > 5MB )")
            
            # Check file extension
            ext = os.path.splitext(self.image.name)[1].lower()
            valid_extensions = ['.jpg', '.jpeg', '.png']
            if ext not in valid_extensions:
                raise ValidationError(f"Unsupported file extension. Allowed: {', '.join(valid_extensions)}")


# =============================================
# AUDIT LOG MODEL
# =============================================

class AuditLog(models.Model):
    """Immutable audit trail for all changes"""
    
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('open_operation', 'Open Operation'),
        ('close_operation', 'Close Operation'),
        ('reopen_operation', 'Reopen Operation'),
        ('export', 'Export Data'),
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('password_change', 'Password Change'),
    ]
    
    TARGET_TYPE_CHOICES = [
        ('record', 'Record'),
        ('operation', 'Operation'),
        ('user', 'User'),
        ('media', 'Media'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action_type = models.CharField(max_length=50, choices=ACTION_CHOICES)
    target_type = models.CharField(max_length=50, choices=TARGET_TYPE_CHOICES)
    target_id = models.IntegerField(help_text="ID of the affected object")
    details = models.JSONField(default=dict, blank=True, help_text="Additional details about the action")
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['target_type', 'target_id']),
        ]
    
    def __str__(self):
        user_str = self.user.username if self.user else "System"
        return f"{user_str} - {self.get_action_type_display()} - {self.timestamp}"


# =============================================
# DELETION LOG MODEL
# =============================================

class DeletionLog(models.Model):
    """Audit log for tracking deletions of operations and records"""
    
    ITEM_TYPE_CHOICES = [
        ('operation', 'Operation'),
        ('record', 'Record'),
    ]
    
    # Who deleted it
    deleted_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='deletions_performed'
    )
    
    # What was deleted
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES)
    item_id = models.IntegerField(help_text="ID of the deleted item")
    item_name = models.CharField(max_length=255, help_text="Name/identifier of deleted item")
    
    # Why and when
    deletion_reason = models.TextField(blank=True, help_text="Reason for deletion")
    deleted_at = models.DateTimeField(auto_now_add=True)
    
    # Additional context
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional data (e.g., record count, associated records, etc.)"
    )
    
    class Meta:
        verbose_name = 'Deletion Log'
        verbose_name_plural = 'Deletion Logs'
        ordering = ['-deleted_at']
        indexes = [
            models.Index(fields=['-deleted_at']),
            models.Index(fields=['item_type', '-deleted_at']),
            models.Index(fields=['deleted_by', '-deleted_at']),
        ]
    
    def __str__(self):
        user_str = self.deleted_by.username if self.deleted_by else "System"
        return f"{user_str} deleted {self.get_item_type_display()}: {self.item_name} on {self.deleted_at.strftime('%Y-%m-%d %H:%M')}"
