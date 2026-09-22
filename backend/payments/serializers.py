from rest_framework import serializers
from .models import Payment, Transaction
from accounts.serializers import UserSummarySerializer


class PaymentSerializer(serializers.ModelSerializer):
    payer = UserSummarySerializer(read_only=True)
    payee = UserSummarySerializer(read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'contract', 'milestone', 'service_order', 'payer', 'payee',
            'amount', 'currency', 'razorpay_order_id', 'razorpay_payment_id',
            'status', 'created_at'
        ]


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'user', 'payment', 'transaction_type', 'amount', 'status', 'description', 'created_at']
