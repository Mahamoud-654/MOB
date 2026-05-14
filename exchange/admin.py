from django.contrib import admin
from .models import DepositRequest, WithdrawalRequest


@admin.register(DepositRequest)
class DepositRequestAdmin(admin.ModelAdmin):
    list_display = ['pk', 'user_id', 'phone_number', 'wallet', 'amount', 'status', 'created_at']
    list_filter = ['status', 'wallet']
    search_fields = ['user_id', 'phone_number', 'transaction_id']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ['pk', 'user_id', 'wallet', 'wallet_number', 'amount', 'status', 'created_at']
    list_filter = ['status', 'wallet']
    search_fields = ['user_id', 'withdrawal_code', 'wallet_number']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
