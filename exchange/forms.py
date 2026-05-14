from django import forms
from .models import DepositRequest, WithdrawalRequest, WALLET_CHOICES


class DepositForm(forms.ModelForm):
    class Meta:
        model = DepositRequest
        fields = ['user_id', 'phone_number', 'wallet', 'transaction_id', 'screenshot', 'amount']
        widgets = {
            'user_id': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Votre ID 1xbet (ex: 123456789)',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Votre numéro de téléphone',
            }),
            'wallet': forms.Select(attrs={
                'class': 'form-select',
            }),
            'transaction_id': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'ID de la transaction',
            }),
            'screenshot': forms.FileInput(attrs={
                'class': 'form-file',
                'accept': 'image/*',
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Montant en DJF',
                'min': '1',
                'step': '1',
            }),
        }
        labels = {
            'user_id': 'ID Utilisateur 1xbet',
            'phone_number': 'Numéro de téléphone',
            'wallet': 'Wallet utilisé',
            'transaction_id': 'ID de transaction',
            'screenshot': "Capture d'écran de la transaction",
            'amount': 'Montant envoyé (DJF)',
        }


class WithdrawalForm(forms.ModelForm):
    class Meta:
        model = WithdrawalRequest
        fields = ['user_id', 'withdrawal_code', 'amount', 'wallet', 'wallet_number']
        widgets = {
            'user_id': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Votre ID 1xbet (ex: 123456789)',
            }),
            'withdrawal_code': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Code de retrait 1xbet',
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Montant à retirer en DJF',
                'min': '1',
                'step': '1',
            }),
            'wallet': forms.Select(attrs={
                'class': 'form-select',
                'id': 'wallet-select',
            }),
            'wallet_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Votre numéro de wallet',
                'id': 'wallet-number',
            }),
        }
        labels = {
            'user_id': 'ID Utilisateur 1xbet',
            'withdrawal_code': 'Code de retrait',
            'amount': 'Montant à retirer (DJF)',
            'wallet': 'Wallet de réception',
            'wallet_number': 'Numéro du wallet',
        }
