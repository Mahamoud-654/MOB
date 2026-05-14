from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('depot/', views.deposit, name='deposit'),
    path('depot/succes/<int:pk>/', views.deposit_success, name='deposit_success'),
    path('retrait/', views.withdrawal, name='withdrawal'),
    path('retrait/succes/<int:pk>/', views.withdrawal_success, name='withdrawal_success'),
    path('admin-dashboard/login/', views.admin_login, name='admin_login'),
    path('admin-dashboard/logout/', views.admin_logout, name='admin_logout'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/depot/<int:pk>/statut/', views.update_deposit_status, name='update_deposit_status'),
    path('admin-dashboard/retrait/<int:pk>/statut/', views.update_withdrawal_status, name='update_withdrawal_status'),
]
