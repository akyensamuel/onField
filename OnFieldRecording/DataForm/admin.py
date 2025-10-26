from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import UserProfile, Operation, Record, RecordMedia, AuditLog, DeletionLog


# =============================================
# USER PROFILE INLINE FOR USER ADMIN
# =============================================

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    fields = ['role', 'employee_id', 'phone_number']


# =============================================
# EXTENDED USER ADMIN
# =============================================

class CustomUserAdmin(BaseUserAdmin):
    """Extended User admin to include profile information inline"""
    inlines = (UserProfileInline,)
    list_display = ['username', 'email', 'first_name', 'last_name', 'get_role', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active', 'groups', 'profile__role']
    
    def get_role(self, obj):
        if hasattr(obj, 'profile'):
            role = obj.profile.role
            colors = {'admin': 'purple', 'staff': 'blue'}
            color = colors.get(role, 'gray')
            return format_html(
                '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 3px;">{}</span>',
                color, obj.profile.get_role_display()
            )
        return '-'
    get_role.short_description = 'Role'
    get_role.admin_order_field = 'profile__role'


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# =============================================
# USER PROFILE ADMIN (Standalone - Optional)
# =============================================

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role_badge', 'employee_id', 'phone_number', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['user__username', 'user__email', 'employee_id', 'phone_number']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'role')
        }),
        ('Additional Details', {
            'fields': ('employee_id', 'phone_number')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def role_badge(self, obj):
        colors = {'admin': 'purple', 'staff': 'blue'}
        color = colors.get(obj.role, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_role_display()
        )
    role_badge.short_description = 'Role'


# =============================================
# OPERATION ADMIN
# =============================================

class RecordInline(admin.TabularInline):
    model = Record
    extra = 0
    fields = ['record_number', 'customer_name', 'status', 'created_by', 'created_at']
    readonly_fields = ['record_number', 'created_at']
    can_delete = False
    max_num = 10
    show_change_link = True


@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    list_display = ['name', 'status_badge', 'total_records_count', 'created_by', 'created_at', 'duration']
    list_filter = ['is_active', 'is_deleted', 'created_at']
    search_fields = ['name', 'description', 'created_by__username']
    readonly_fields = ['created_at', 'updated_at', 'next_record_seq', 'closed_at', 'closed_by']
    inlines = [RecordInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'created_by')
        }),
        ('Status', {
            'fields': ('is_active', 'is_deleted')
        }),
        ('Timeline', {
            'fields': ('start_at', 'end_at', 'closed_at', 'closed_by')
        }),
        ('System Fields', {
            'fields': ('next_record_seq', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        if obj.is_deleted:
            color = 'gray'
            text = 'DELETED'
        elif obj.is_active:
            color = 'green'
            text = 'ACTIVE'
        else:
            color = 'red'
            text = 'CLOSED'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, text
        )
    status_badge.short_description = 'Status'
    
    def total_records_count(self, obj):
        return obj.total_records
    total_records_count.short_description = 'Total Records'
    
    def duration(self, obj):
        days = obj.duration_days
        if days == 0:
            return 'Just started'
        return f"{days} day{'s' if days != 1 else ''}"
    duration.short_description = 'Duration'
    
    actions = ['activate_operation', 'close_operation']
    
    def activate_operation(self, request, queryset):
        for operation in queryset:
            try:
                operation.reopen_operation()
                self.message_user(request, f"Operation '{operation.name}' has been activated.")
            except Exception as e:
                self.message_user(request, f"Error activating '{operation.name}': {str(e)}", level='error')
    activate_operation.short_description = "Activate selected operations"
    
    def close_operation(self, request, queryset):
        for operation in queryset:
            operation.close_operation(request.user)
            self.message_user(request, f"Operation '{operation.name}' has been closed.")
    close_operation.short_description = "Close selected operations"


# =============================================
# RECORD ADMIN
# =============================================

class RecordMediaInline(admin.TabularInline):
    model = RecordMedia
    extra = 1
    fields = ['image', 'file_size_display', 'is_processed', 'ocr_result']
    readonly_fields = ['file_size_display']
    
    def file_size_display(self, obj):
        if obj.file_size:
            size_kb = obj.file_size / 1024
            if size_kb < 1024:
                return f"{size_kb:.2f} KB"
            else:
                return f"{size_kb/1024:.2f} MB"
        return "N/A"
    file_size_display.short_description = 'File Size'


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ['record_number', 'customer_name', 'operation', 'status_badge', 'anomaly_badge', 
                    'has_gps_icon', 'created_by', 'created_at']
    list_filter = ['status', 'type_of_anomaly', 'operation', 'created_at']
    search_fields = ['record_number', 'customer_name', 'customer_contact', 
                     'account_number', 'meter_number']
    readonly_fields = ['record_number', 'created_at', 'updated_at']
    inlines = [RecordMediaInline]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Record Information', {
            'fields': ('operation', 'record_number', 'status')
        }),
        ('Customer Details', {
            'fields': ('customer_name', 'customer_contact', 'account_number')
        }),
        ('GPS Location', {
            'fields': ('gps_latitude', 'gps_longitude', 'gps_address'),
            'classes': ('collapse',)
        }),
        ('Meter Information', {
            'fields': ('meter_number', 'meter_reading', 'todays_balance')
        }),
        ('Anomaly & Notes', {
            'fields': ('type_of_anomaly', 'remarks')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at', 'is_deleted'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'draft': 'gray',
            'submitted': 'blue',
            'verified': 'green'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def anomaly_badge(self, obj):
        if obj.has_anomaly:
            return format_html(
                '<span style="background-color: orange; color: white; padding: 2px 8px; border-radius: 3px;">{}</span>',
                obj.get_type_of_anomaly_display()
            )
        return format_html('<span style="color: green;">✓ No Anomaly</span>')
    anomaly_badge.short_description = 'Anomaly'
    
    def has_gps_icon(self, obj):
        if obj.has_gps:
            return format_html('<span style="color: green; font-size: 16px;">📍</span>')
        return format_html('<span style="color: gray;">-</span>')
    has_gps_icon.short_description = 'GPS'


# =============================================
# RECORD MEDIA ADMIN
# =============================================

@admin.register(RecordMedia)
class RecordMediaAdmin(admin.ModelAdmin):
    list_display = ['record', 'image_thumbnail', 'file_size_display', 'is_processed', 
                    'uploaded_by', 'uploaded_at']
    list_filter = ['is_processed', 'uploaded_at']
    search_fields = ['record__record_number', 'record__customer_name']
    readonly_fields = ['file_size', 'uploaded_at', 'image_preview']
    
    fieldsets = (
        ('Media Information', {
            'fields': ('record', 'image', 'image_preview')
        }),
        ('Processing', {
            'fields': ('is_processed', 'ocr_result', 'ocr_confidence')
        }),
        ('Metadata', {
            'fields': ('uploaded_by', 'uploaded_at', 'file_size'),
            'classes': ('collapse',)
        }),
    )
    
    def image_thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', 
                             obj.image.url)
        return '-'
    image_thumbnail.short_description = 'Thumbnail'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="300" style="max-width: 100%;" />', 
                             obj.image.url)
        return 'No image'
    image_preview.short_description = 'Preview'
    
    def file_size_display(self, obj):
        if obj.file_size:
            size_kb = obj.file_size / 1024
            if size_kb < 1024:
                return f"{size_kb:.2f} KB"
            else:
                return f"{size_kb/1024:.2f} MB"
        return "N/A"
    file_size_display.short_description = 'File Size'


# =============================================
# AUDIT LOG ADMIN
# =============================================

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'user', 'action_type_badge', 'target_type', 'target_id', 'ip_address']
    list_filter = ['action_type', 'target_type', 'timestamp']
    search_fields = ['user__username', 'ip_address', 'details']
    readonly_fields = ['user', 'action_type', 'target_type', 'target_id', 'details', 
                       'timestamp', 'ip_address', 'details_display']
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Action Information', {
            'fields': ('user', 'action_type', 'timestamp', 'ip_address')
        }),
        ('Target', {
            'fields': ('target_type', 'target_id')
        }),
        ('Details', {
            'fields': ('details_display',)
        }),
    )
    
    def has_add_permission(self, request):
        # Audit logs should not be manually created
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Audit logs should not be deleted
        return False
    
    def action_type_badge(self, obj):
        colors = {
            'create': 'green',
            'update': 'blue',
            'delete': 'red',
            'open_operation': 'purple',
            'close_operation': 'orange',
            'reopen_operation': 'teal',
            'export': 'gray',
        }
        color = colors.get(obj.action_type, 'black')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_action_type_display()
        )
    action_type_badge.short_description = 'Action'
    
    def details_display(self, obj):
        import json
        try:
            formatted = json.dumps(obj.details, indent=2)
            return format_html('<pre style="background: #f5f5f5; padding: 10px; border-radius: 5px;">{}</pre>', 
                             formatted)
        except:
            return str(obj.details)
    details_display.short_description = 'Details (JSON)'


# =============================================
# DELETION LOG ADMIN
# =============================================

@admin.register(DeletionLog)
class DeletionLogAdmin(admin.ModelAdmin):
    list_display = ['deleted_at', 'deleted_by', 'item_type_badge', 'item_name', 'deletion_reason_short']
    list_filter = ['item_type', 'deleted_at', 'deleted_by']
    search_fields = ['item_name', 'deletion_reason', 'deleted_by__username']
    readonly_fields = ['deleted_by', 'item_type', 'item_id', 'item_name', 'deletion_reason', 
                       'deleted_at', 'metadata_display']
    date_hierarchy = 'deleted_at'
    
    fieldsets = (
        ('Deletion Information', {
            'fields': ('deleted_by', 'deleted_at', 'deletion_reason')
        }),
        ('Deleted Item', {
            'fields': ('item_type', 'item_id', 'item_name')
        }),
        ('Additional Context', {
            'fields': ('metadata_display',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Deletion logs should not be manually created
        return False
    
    def has_change_permission(self, request, obj=None):
        # Deletion logs are read-only
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Deletion logs should not be deleted
        return request.user.is_superuser  # Only superusers can delete logs
    
    def item_type_badge(self, obj):
        colors = {
            'operation': 'purple',
            'record': 'blue',
        }
        color = colors.get(obj.item_type, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_item_type_display()
        )
    item_type_badge.short_description = 'Item Type'
    
    def deletion_reason_short(self, obj):
        if obj.deletion_reason:
            reason = obj.deletion_reason[:50]
            if len(obj.deletion_reason) > 50:
                reason += '...'
            return reason
        return '-'
    deletion_reason_short.short_description = 'Reason'
    
    def metadata_display(self, obj):
        import json
        try:
            formatted = json.dumps(obj.metadata, indent=2)
            return format_html('<pre style="background: #f5f5f5; padding: 10px; border-radius: 5px;">{}</pre>', 
                             formatted)
        except:
            return str(obj.metadata)
    metadata_display.short_description = 'Metadata (JSON)'
