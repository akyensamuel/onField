"""
Django forms for DataForm app
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from .models import Operation, Record, RecordMedia


class CustomLoginForm(AuthenticationForm):
    """Custom login form with styling"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Username',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Password'
        })
    )


class CustomPasswordChangeForm(PasswordChangeForm):
    """Custom password change form"""
    old_password = forms.CharField(
        label="Current Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Current Password'
        })
    )
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'New Password'
        })
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm New Password'
        })
    )


class OperationForm(forms.ModelForm):
    """Form for creating/editing operations"""
    
    class Meta:
        model = Operation
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Operation Name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 4,
                'placeholder': 'Operation Description (optional)'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            })
        }
        help_texts = {
            'is_active': 'Note: Only one operation can be active at a time.'
        }


class RecordForm(forms.ModelForm):
    """Form for creating/editing field records"""
    
    class Meta:
        model = Record
        fields = [
            'customer_name', 'customer_contact', 'account_number', 
            'meter_number', 'meter_reading', 'todays_balance',
            'gps_latitude', 'gps_longitude', 'gps_address',
            'type_of_anomaly', 'remarks', 'status'
        ]
        widgets = {
            'customer_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Customer Name'
            }),
            'customer_contact': forms.TextInput(attrs={
                'class': 'form-input',
                'type': 'tel',
                'placeholder': '+1234567890'
            }),
            'account_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Account Number'
            }),
            'meter_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Meter Number'
            }),
            'meter_reading': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'todays_balance': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'gps_latitude': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.0000001',
                'placeholder': 'Latitude',
                'readonly': True
            }),
            'gps_longitude': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.0000001',
                'placeholder': 'Longitude',
                'readonly': True
            }),
            'gps_address': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 2,
                'placeholder': 'e.g., AH-2324-2424 or street address'
            }),
            'type_of_anomaly': forms.Select(attrs={
                'class': 'form-select'
            }),
            'remarks': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'Additional remarks or notes'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            })
        }
        labels = {
            'customer_contact': 'Customer Contact (Phone)',
            'todays_balance': "Today's Balance",
            'gps_latitude': 'GPS Latitude',
            'gps_longitude': 'GPS Longitude',
            'gps_address': 'GPS Address',
        }


class RecordMediaForm(forms.ModelForm):
    """Form for uploading photos to records"""
    
    class Meta:
        model = RecordMedia
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-input',
                'accept': 'image/jpeg,image/png,image/jpg',
                'multiple': False
            })
        }
        labels = {
            'image': 'Upload Photo'
        }
        help_texts = {
            'image': 'Max size: 5MB. Formats: JPG, PNG'
        }


class RecordSearchForm(forms.Form):
    """Form for searching/filtering records"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Search by record number, customer name, account, meter...'
        })
    )
    
    operation = forms.ModelChoiceField(
        queryset=Operation.objects.filter(is_deleted=False).order_by('-created_at'),
        required=False,
        empty_label='All Operations',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + Record.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    anomaly = forms.ChoiceField(
        choices=[('', 'All Anomalies')] + Record.ANOMALY_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date'
        })
    )
