"""
URL configuration for DataForm app
"""

from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('password/change/', views.change_password, name='password_change'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Operations (Admin)
    path('operations/', views.operation_list, name='operation_list'),
    path('operations/create/', views.operation_create, name='operation_create'),
    path('operations/<int:pk>/', views.operation_detail, name='operation_detail'),
    path('operations/<int:pk>/activate/', views.operation_activate, name='operation_activate'),
    path('operations/<int:pk>/close/', views.operation_close, name='operation_close'),
    path('operations/<int:pk>/delete/', views.operation_delete, name='operation_delete'),
    path('operations/<int:pk>/export/pdf/', views.operation_export_pdf, name='operation_export_pdf'),
    path('operations/<int:pk>/export/xlsx/', views.operation_export_xlsx, name='operation_export_xlsx'),
    path('operations/<int:pk>/search/', views.operation_search, name='operation_search'),
    
    # Search (Admin only)
    path('search/', views.system_search, name='system_search'),
    
    # Records
    path('records/', views.record_list, name='record_list'),
    path('records/create/', views.record_create, name='record_create'),
    path('records/<int:pk>/', views.record_detail, name='record_detail'),
    path('records/<int:pk>/edit/', views.record_update, name='record_update'),
    path('records/<int:pk>/delete/', views.record_delete, name='record_delete'),
    
    # API
    path('api/active-operation/', views.get_active_operation, name='api_active_operation'),
]
