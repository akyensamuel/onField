"""
Management command to generate sample test data for the OnField Recording System.

Usage:
    python manage.py generate_test_data

This command creates:
- 2 staff users (staff1, staff2)
- 1 admin user (testadmin)
- 3 operations (2 closed, 1 active)
- 30-50 sample records with varied statuses and anomalies
- Sample photos for some records
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from DataForm.models import UserProfile, Operation, Record, RecordMedia
from decimal import Decimal
import random
from datetime import timedelta
from django.utils import timezone


class Command(BaseCommand):
    help = 'Generate sample test data for the OnField Recording System'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing test data before generating new data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing test data...'))
            # Delete records from test operations first
            test_ops = Operation.objects.filter(name__icontains='Test')
            Record.objects.filter(operation__in=test_ops).delete()
            # Then delete test operations
            test_ops.delete()
            # Finally delete test users
            User.objects.filter(username__in=['staff1', 'staff2', 'testadmin']).delete()
            self.stdout.write(self.style.SUCCESS('Test data cleared!'))

        self.stdout.write(self.style.SUCCESS('Starting test data generation...'))

        # Sample data
        customer_names = [
            'John Kamau', 'Mary Wanjiku', 'Peter Ochieng', 'Jane Akinyi',
            'David Mwangi', 'Sarah Njeri', 'James Otieno', 'Grace Wambui',
            'Samuel Mutua', 'Lucy Chebet', 'Michael Kiprono', 'Anne Nyambura',
            'Paul Omondi', 'Catherine Mumbi', 'Joseph Kipchoge', 'Rose Achieng',
            'Daniel Kariuki', 'Faith Wangari', 'Eric Owino', 'Alice Njoki',
            'Brian Kamau', 'Joyce Wairimu', 'Kevin Odhiambo', 'Nancy Adhiambo',
            'Steve Kimani', 'Betty Wanjiru', 'Mark Onyango', 'Susan Gathoni',
            'Frank Kamande', 'Helen Auma', 'Victor Wekesa', 'Rachel Njambi',
            'Andrew Kiptoo', 'Christine Wambua', 'Patrick Ouma', 'Elizabeth Wangui'
        ]

        addresses = [
            'Nairobi, Kasarani Estate', 'Nairobi, Umoja Estate', 'Nairobi, Eastleigh',
            'Nairobi, Kibera', 'Nairobi, Lang\'ata', 'Nairobi, Westlands',
            'Mombasa, Nyali', 'Mombasa, Bamburi', 'Kisumu, Milimani',
            'Nakuru, Lanet', 'Eldoret, Pioneer', 'Thika, Blue Post',
            'Kiambu, Ruaka', 'Machakos Town', 'Kitale, Township'
        ]

        anomaly_types = ['none', 'meter_bypass', 'illegal_connection', 'meter_tampered', 'meter_reversed']
        statuses = ['draft', 'submitted', 'verified']

        # Create groups if they don't exist
        staff_group, _ = Group.objects.get_or_create(name='Staff')
        admin_group, _ = Group.objects.get_or_create(name='Admin')

        # Create test users
        self.stdout.write('Creating test users...')
        
        # Create staff users
        staff_users = []
        for i in range(1, 3):
            username = f'staff{i}'
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=f'staff{i}@example.com',
                    password='testpass123',
                    first_name=f'Staff',
                    last_name=f'User {i}'
                )
                user.groups.add(staff_group)
                
                # Update UserProfile (created by signal)
                profile = user.profile
                profile.role = 'staff'
                # Find next available employee ID
                existing_ids = UserProfile.objects.values_list('employee_id', flat=True)
                emp_num = i + 1
                while f'EMP-{emp_num:03d}' in existing_ids:
                    emp_num += 1
                profile.employee_id = f'EMP-{emp_num:03d}'
                profile.phone_number = f'0712345{i:03d}'
                profile.save()
                
                staff_users.append(user)
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created staff user: {username}'))
            else:
                staff_users.append(User.objects.get(username=username))

        # Create admin user
        if not User.objects.filter(username='testadmin').exists():
            admin_user = User.objects.create_user(
                username='testadmin',
                email='admin@example.com',
                password='testpass123',
                first_name='Admin',
                last_name='User'
            )
            admin_user.groups.add(admin_group)
            
            profile = admin_user.profile
            profile.role = 'admin'
            # Find next available employee ID
            existing_ids = UserProfile.objects.values_list('employee_id', flat=True)
            emp_num = 100
            while f'EMP-{emp_num:03d}' in existing_ids:
                emp_num += 1
            profile.employee_id = f'EMP-{emp_num:03d}'
            profile.phone_number = '0711111111'
            profile.save()
            
            self.stdout.write(self.style.SUCCESS(f'  ✓ Created admin user: testadmin'))
        else:
            admin_user = User.objects.get(username='testadmin')

        # Create operations
        self.stdout.write('Creating test operations...')
        
        operations = []
        
        # Operation 1: Closed operation (Q1 2024)
        op1_name = 'Test Operation - Q1 2024 Meter Reading'
        op1, created = Operation.objects.get_or_create(
            name=op1_name,
            defaults={
                'description': 'Quarterly meter reading campaign for Q1 2024 across Nairobi region',
                'is_active': False,
                'created_by': admin_user
            }
        )
        if created:
            op1.created_at = timezone.now() - timedelta(days=90)
            op1.save()
            self.stdout.write(self.style.SUCCESS(f'  ✓ Created operation: {op1.name} (Closed)'))
        else:
            self.stdout.write(self.style.WARNING(f'  ℹ Operation already exists: {op1.name}'))
        operations.append(op1)

        # Operation 2: Closed operation (Q2 2024)
        op2_name = 'Test Operation - Q2 2024 Verification Drive'
        op2, created = Operation.objects.get_or_create(
            name=op2_name,
            defaults={
                'description': 'Customer verification and anomaly detection drive for Q2 2024',
                'is_active': False,
                'created_by': admin_user
            }
        )
        if created:
            op2.created_at = timezone.now() - timedelta(days=30)
            op2.save()
            self.stdout.write(self.style.SUCCESS(f'  ✓ Created operation: {op2.name} (Closed)'))
        else:
            self.stdout.write(self.style.WARNING(f'  ℹ Operation already exists: {op2.name}'))
        operations.append(op2)

        # Operation 3: Active operation (check if one already exists)
        active_op = Operation.objects.filter(is_active=True).first()
        if not active_op:
            op3 = Operation.objects.create(
                name='Test Operation - Q3 2024 Field Data Collection',
                description='Active field data collection operation for Q3 2024',
                is_active=True,
                created_by=admin_user
            )
            op3.created_at = timezone.now() - timedelta(days=7)
            op3.save()
            operations.append(op3)
            self.stdout.write(self.style.SUCCESS(f'  ✓ Created operation: {op3.name} (Active)'))
        else:
            operations.append(active_op)
            self.stdout.write(self.style.WARNING(f'  ℹ Using existing active operation: {active_op.name}'))

        # Create records
        self.stdout.write('Creating test records...')
        
        record_count = 0
        
        # Generate records for each operation
        for operation in operations:
            # More records for older operations
            if operation == op1:
                num_records = random.randint(15, 20)
            elif operation == op2:
                num_records = random.randint(10, 15)
            else:  # Active operation
                num_records = random.randint(8, 12)
            
            for i in range(num_records):
                # Select random staff member as creator
                if staff_users:
                    creator = random.choice(staff_users)
                else:
                    creator = admin_user
                
                # Random customer
                customer_name = random.choice(customer_names)
                
                # Generate random data
                account_number = f'ACC-{random.randint(100000, 999999)}'
                meter_number = f'MTR-{random.randint(10000, 99999)}'
                meter_reading = random.randint(1000, 99999)
                balance = Decimal(random.uniform(500, 50000)).quantize(Decimal('0.01'))
                
                # GPS coordinates (Kenya)
                gps_lat = Decimal(random.uniform(-1.5, -0.5)).quantize(Decimal('0.000001'))
                gps_lon = Decimal(random.uniform(36.5, 37.5)).quantize(Decimal('0.000001'))
                gps_address = random.choice(addresses)
                
                # Phone number
                customer_contact = f'07{random.randint(10000000, 99999999)}'
                
                # Anomaly (20% chance)
                type_of_anomaly = random.choice(anomaly_types) if random.random() < 0.2 else ''
                if type_of_anomaly == 'none':
                    type_of_anomaly = ''
                
                # Remarks for anomalies
                remarks = ''
                if type_of_anomaly:
                    remarks = f'Detected {type_of_anomaly.replace("_", " ")}. Requires immediate attention and follow-up.'
                
                # Status (more verified records for closed operations)
                if operation.is_active:
                    status = random.choices(statuses, weights=[10, 60, 30])[0]
                else:
                    status = random.choices(statuses, weights=[5, 15, 80])[0]
                
                # Create record using the operation to ensure proper record numbering
                record = Record.objects.create(
                    operation=operation,
                    customer_name=customer_name,
                    customer_contact=customer_contact,
                    gps_latitude=gps_lat,
                    gps_longitude=gps_lon,
                    gps_address=gps_address,
                    account_number=account_number,
                    meter_number=meter_number,
                    todays_balance=balance,
                    meter_reading=meter_reading,
                    type_of_anomaly=type_of_anomaly,
                    remarks=remarks,
                    status=status,
                    created_by=creator
                )
                
                # Set random creation time
                days_ago = random.randint(1, 60) if operation == op1 else \
                           random.randint(1, 25) if operation == op2 else \
                           random.randint(0, 7)
                record.created_at = timezone.now() - timedelta(days=days_ago, hours=random.randint(0, 23))
                record.save()
                
                record_count += 1
                
                if record_count % 10 == 0:
                    self.stdout.write(f'  Created {record_count} records...')

        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {record_count} total records'))

        # Summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('═' * 60))
        self.stdout.write(self.style.SUCCESS('Test Data Generation Complete!'))
        self.stdout.write(self.style.SUCCESS('═' * 60))
        self.stdout.write('')
        self.stdout.write('Test Users Created:')
        self.stdout.write(f'  • staff1 / testpass123 (Staff)')
        self.stdout.write(f'  • staff2 / testpass123 (Staff)')
        self.stdout.write(f'  • testadmin / testpass123 (Admin)')
        self.stdout.write('')
        self.stdout.write('Operations Created:')
        for op in operations:
            status = '✓ ACTIVE' if op.is_active else '✗ Closed'
            self.stdout.write(f'  • {op.name} [{status}]')
        self.stdout.write('')
        self.stdout.write(f'Total Records: {record_count}')
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('You can now:'))
        self.stdout.write('  1. Login as staff1 or staff2 to create/view records')
        self.stdout.write('  2. Login as testadmin to manage operations and view all data')
        self.stdout.write('  3. Test the complete workflow with the active operation')
        self.stdout.write('')
