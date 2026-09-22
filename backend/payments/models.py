from django.db import models
from django.conf import settings
from proposals.models import Contract
from projects.models import Milestone
from services.models import ServiceOrder


class Payment(models.Model):
    class Status(models.TextChoices):
        CREATED = 'created', 'Order Created'
        ESCROW_FUNDED = 'escrow_funded', 'Held in Escrow'
        RELEASED = 'released', 'Released to Freelancer/Team'
        REFUNDED = 'refunded', 'Refunded'
        FAILED = 'failed', 'Failed'

    contract = models.ForeignKey(Contract, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    milestone = models.ForeignKey(Milestone, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    service_order = models.ForeignKey(ServiceOrder, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    payer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments_made')
    payee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments_received')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default='INR')
    razorpay_order_id = models.CharField(max_length=100, blank=True, default='')
    razorpay_payment_id = models.CharField(max_length=100, blank=True, default='')
    razorpay_signature = models.CharField(max_length=255, blank=True, default='')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CREATED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment #{self.id} (${self.amount}) - {self.get_status_display()}"


class Transaction(models.Model):
    class TxType(models.TextChoices):
        ESCROW_DEPOSIT = 'escrow_deposit', 'Escrow Deposit'
        PAYOUT = 'payout', 'Milestone Payout'
        SERVICE_PURCHASE = 'service_purchase', 'Service Package Order'
        REFUND = 'refund', 'Refund'
        PLATFORM_FEE = 'platform_fee', 'Platform Commission'

    class Status(models.TextChoices):
        SUCCESS = 'success', 'Success'
        PENDING = 'pending', 'Pending'
        FAILED = 'failed', 'Failed'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    transaction_type = models.CharField(max_length=30, choices=TxType.choices, default=TxType.ESCROW_DEPOSIT)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUCCESS)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_transaction_type_display()}: ${self.amount} for {self.user.username}"
