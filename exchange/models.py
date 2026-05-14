from django.db import models
from django.utils import timezone


WALLET_CHOICES = [
    ('waafi', 'Waafi'),
    ('cac', 'CAC'),
    ('d-money', 'D-Money'),
    ('saba', 'Saba'),
]

STATUS_CHOICES = [
    ('pending', 'En attente'),
    ('approved', 'Approuvé'),
    ('rejected', 'Rejeté'),
]


class DepositRequest(models.Model):
    user_id = models.CharField(max_length=100, verbose_name="ID Utilisateur 1xbet")
    phone_number = models.CharField(max_length=20, verbose_name="Numéro de téléphone")
    wallet = models.CharField(max_length=20, choices=WALLET_CHOICES, verbose_name="Wallet utilisé")
    transaction_id = models.CharField(max_length=200, verbose_name="ID de transaction")
    screenshot = models.ImageField(upload_to='deposits/screenshots/', verbose_name="Capture d'écran")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Montant (DJF)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    admin_note = models.TextField(blank=True, verbose_name="Note administrateur")

    class Meta:
        verbose_name = "Demande de dépôt"
        verbose_name_plural = "Demandes de dépôt"
        ordering = ['-created_at']

    def __str__(self):
        return f"Dépôt #{self.pk} - {self.user_id} - {self.amount} DJF ({self.get_status_display()})"


class WithdrawalRequest(models.Model):
    user_id = models.CharField(max_length=100, verbose_name="ID Utilisateur 1xbet")
    withdrawal_code = models.CharField(max_length=200, verbose_name="Code de retrait")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Montant (DJF)")
    wallet = models.CharField(max_length=20, choices=WALLET_CHOICES, verbose_name="Wallet de réception")
    wallet_number = models.CharField(max_length=30, verbose_name="Numéro du wallet")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    admin_note = models.TextField(blank=True, verbose_name="Note administrateur")

    class Meta:
        verbose_name = "Demande de retrait"
        verbose_name_plural = "Demandes de retrait"
        ordering = ['-created_at']

    def __str__(self):
        return f"Retrait #{self.pk} - {self.user_id} - {self.amount} DJF ({self.get_status_display()})"
