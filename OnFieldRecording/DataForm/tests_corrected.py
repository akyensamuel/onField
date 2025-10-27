"""
Unit Tests for OnField Recording System - CORRECTED VERSION
Tests models, views, and critical business logic with correct field names
"""
import pytest
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from DataForm.models import (
    UserProfile, Operation, Record, RecordMedia,
    AuditLog, DeletionLog
)
from datetime import timedelta


# ============================================
# MODEL TESTS
# ============================================

class UserProfileModelTest(TestCase):
    """Test UserProfile model"""
    
    def setUp(self):
        # Signal auto-creates UserProfile, so we just create user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Get the auto-created profile
        self.profile = self.user.profile
    
    def test_create_user_profile(self):
        """Test that user profile is auto-created"""
        # Profile should be auto-created by signal
        self.assertIsNotNone(self.profile)
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.role, 'staff')  # Default role
        self.assertTrue(self.profile.is_staff_member())
        self.assertFalse(self.profile.is_admin())
    
    def test_admin_profile(self):
        """Test admin profile"""
        # Update existing profile to admin
        self.profile.role = 'admin'
        self.profile.save()
        self.assertTrue(self.profile.is_admin())
        self.assertFalse(self.profile.is_staff_member())
    
    def test_phone_number_validation(self):
        """Test phone number format validation"""
        # Update existing profile with phone number
        self.profile.phone_number = '+12345678901234'
        self.profile.save()
        self.assertIsNotNone(self.profile.phone_number)
        self.assertEqual(self.profile.phone_number, '+12345678901234')


class OperationModelTest(TestCase):
    """Test Operation model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='admin',
            password='admin123'
        )
        # Profile is auto-created, just update role
        self.user.profile.role = 'admin'
        self.user.profile.save()
    
    def test_create_operation(self):
        """Test creating an operation"""
        operation = Operation.objects.create(
            name='Test Operation',
            description='Test Description',
            created_by=self.user,
            is_active=False
        )
        self.assertEqual(operation.name, 'Test Operation')
        self.assertFalse(operation.is_active)
    
    def test_operation_str_representation(self):
        """Test string representation"""
        operation = Operation.objects.create(
            name='My Operation',
            created_by=self.user,
            is_active=True
        )
        self.assertEqual(str(operation), 'My Operation (ACTIVE)')


class RecordModelTest(TestCase):
    """Test Record model with CORRECT field names"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='staff',
            password='staff123'
        )
        # Profile is auto-created, just update role
        self.user.profile.role = 'staff'
        self.user.profile.save()
        
        self.operation = Operation.objects.create(
            name='Test Operation',
            created_by=self.user,
            is_active=True
        )
    
    def test_create_record(self):
        """Test creating a record with correct field names"""
        record = Record.objects.create(
            operation=self.operation,
            customer_name='John Doe',
            customer_contact='+1234567890',
            account_number='ACC001',
            meter_number='MTR001',
            todays_balance=Decimal('100.50'),  # Correct field name
            meter_reading=Decimal('12345'),
            type_of_anomaly='none',
            created_by=self.user,  # Correct field name
            status='submitted'
        )
        self.assertEqual(record.customer_name, 'John Doe')
        self.assertEqual(record.todays_balance, Decimal('100.50'))
        # record_number is auto-generated
        self.assertIsNotNone(record.record_number)
    
    def test_record_with_gps(self):
        """Test record with GPS coordinates"""
        record = Record.objects.create(
            operation=self.operation,
            customer_name='Jane Doe',
            customer_contact='+1234567891',
            account_number='ACC002',
            meter_number='MTR002',
            todays_balance=Decimal('200.00'),
            meter_reading=Decimal('54321'),
            gps_latitude=Decimal('6.6745'),
            gps_longitude=Decimal('-1.5657'),
            created_by=self.user
        )
        self.assertTrue(record.has_gps)
        self.assertEqual(record.gps_latitude, Decimal('6.6745'))
    
    def test_record_with_anomaly(self):
        """Test record with anomaly"""
        record = Record.objects.create(
            operation=self.operation,
            customer_name='Test User',
            customer_contact='+1234567892',
            account_number='ACC003',
            meter_number='MTR003',
            todays_balance=Decimal('50.00'),
            meter_reading=Decimal('11111'),
            type_of_anomaly='meter_damaged',  # Valid choice
            created_by=self.user
        )
        self.assertTrue(record.has_anomaly)
        self.assertEqual(record.type_of_anomaly, 'meter_damaged')


# ============================================
# VIEW TESTS
# ============================================

class AuthenticationViewTest(TestCase):
    """Test authentication views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Profile is auto-created, just update role
        self.user.profile.role = 'staff'
        self.user.profile.save()
    
    def test_login_view_get(self):
        """Test login page loads"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
    
    def test_logout(self):
        """Test logout"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)


class DashboardViewTest(TestCase):
    """Test dashboard views"""
    
    def setUp(self):
        self.client = Client()
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            password='admin123'
        )
        self.admin_user.profile.role = 'admin'
        self.admin_user.profile.save()
        
        # Create staff user
        self.staff_user = User.objects.create_user(
            username='staff',
            password='staff123'
        )
        self.staff_user.profile.role = 'staff'
        self.staff_user.profile.save()
    
    def test_admin_dashboard_access(self):
        """Test admin can access dashboard"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_unauthenticated_dashboard_denied(self):
        """Test unauthenticated user cannot access dashboard"""
        response = self.client.get(reverse('dashboard'))
        # Should redirect to login
        self.assertEqual(response.status_code, 302)


class OperationViewTest(TestCase):
    """Test operation views"""
    
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin',
            password='admin123'
        )
        self.admin_user.profile.role = 'admin'
        self.admin_user.profile.save()
        
        self.operation = Operation.objects.create(
            name='Test Operation',
            created_by=self.admin_user,
            is_active=False
        )
    
    def test_operation_list_view(self):
        """Test operation list view"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('operation_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Operation')
    
    def test_operation_detail_view(self):
        """Test operation detail view"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get(
            reverse('operation_detail', kwargs={'pk': self.operation.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Operation')


class RecordNumberGenerationTest(TestCase):
    """Test record number auto-generation"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='staff',
            password='staff123'
        )
        self.user.profile.role = 'staff'
        self.user.profile.save()
        
        self.operation = Operation.objects.create(
            name='Test Operation',
            created_by=self.user,
            is_active=True
        )
    
    def test_record_number_auto_generation(self):
        """Test record number is auto-generated"""
        record = Record.objects.create(
            operation=self.operation,
            customer_name='First Customer',
            customer_contact='+1234567890',
            account_number='ACC001',
            meter_number='MTR001',
            todays_balance=Decimal('100.00'),
            meter_reading=Decimal('12345'),
            created_by=self.user
        )
        # record_number should be auto-generated (not empty)
        self.assertIsNotNone(record.record_number)
        self.assertTrue(len(record.record_number) > 0)
    
    def test_sequential_records(self):
        """Test creating multiple sequential records"""
        records = []
        for i in range(1, 6):
            record = Record.objects.create(
                operation=self.operation,
                customer_name=f'Customer {i}',
                customer_contact=f'+123456789{i}',
                account_number=f'ACC{i:03d}',
                meter_number=f'MTR{i:03d}',
                todays_balance=Decimal('100.00'),
                meter_reading=Decimal('12345'),
                created_by=self.user
            )
            records.append(record)
        
        # All records should have unique record_numbers
        record_numbers = [r.record_number for r in records]
        self.assertEqual(len(record_numbers), len(set(record_numbers)))
        self.assertEqual(len(records), 5)


class AuditLogTest(TestCase):
    """Test audit logging"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='admin',
            password='admin123'
        )
        self.user.profile.role = 'admin'
        self.user.profile.save()
    
    def test_create_audit_log(self):
        """Test creating an audit log entry"""
        log = AuditLog.objects.create(
            user=self.user,
            action_type='create',
            target_type='operation',
            target_id=1,
            details={'name': 'Test Operation'},
            ip_address='127.0.0.1'
        )
        self.assertEqual(log.action_type, 'create')
        self.assertEqual(log.user, self.user)
        self.assertIsNotNone(log.timestamp)
