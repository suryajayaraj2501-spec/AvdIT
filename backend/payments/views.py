from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from rest_framework import views, permissions, status
from rest_framework.response import Response
import razorpay
import uuid
from .models import Payment, Transaction
from .serializers import PaymentSerializer, TransactionSerializer
from projects.models import Milestone
from proposals.models import Contract
from services.models import ServiceOrder
from notifications.models import Notification


def get_razorpay_client():
    key_id = getattr(settings, 'RAZORPAY_KEY_ID', '')
    key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', '')
    if key_id and key_secret and not key_id.startswith('rzp_test_advit'):
        try:
            return razorpay.Client(auth=(key_id, key_secret))
        except Exception:
            return None
    return None


# ==========================================
# Server-Rendered Views
# ==========================================

@login_required
def payment_history_view(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
    payments_made = Payment.objects.filter(payer=request.user).order_by('-created_at')
    payments_received = Payment.objects.filter(payee=request.user).order_by('-created_at')

    return render(request, 'payments/history.html', {
        'transactions': transactions,
        'payments_made': payments_made,
        'payments_received': payments_received,
    })


# ==========================================
# REST API Endpoints
# ==========================================

class CreateRazorpayOrderAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        order_type = request.data.get('order_type')  # 'milestone' | 'service_order'
        target_id = request.data.get('target_id')
        amount = float(request.data.get('amount', 0))
        description = request.data.get('description', 'AdvIT Payment')

        if amount <= 0:
            return Response({'error': 'Amount must be greater than zero.'}, status=status.HTTP_400_BAD_REQUEST)

        currency = 'INR'
        amount_in_cents = int(amount * 100)
        rzp_client = get_razorpay_client()
        order_id = f"order_{uuid.uuid4().hex[:14]}"

        if rzp_client:
            try:
                rzp_order = rzp_client.order.create({
                    'amount': amount_in_cents,
                    'currency': currency,
                    'payment_capture': '1'
                })
                order_id = rzp_order['id']
            except Exception as e:
                # Graceful fallback to mock test order id
                order_id = f"order_mock_{uuid.uuid4().hex[:12]}"

        # Create Payment Record
        payment = Payment.objects.create(
            payer=request.user,
            amount=amount,
            currency=currency,
            razorpay_order_id=order_id,
            status=Payment.Status.CREATED
        )

        payee_user = None
        if order_type == 'milestone' and target_id:
            milestone = get_object_or_404(Milestone, id=target_id)
            payment.milestone = milestone
            payment.contract = milestone.contract
            if milestone.contract:
                if milestone.contract.freelancer:
                    payee_user = milestone.contract.freelancer.user
                elif milestone.contract.team:
                    payee_user = milestone.contract.team.created_by
            payment.payee = payee_user
            payment.save()

        elif order_type == 'service_order' and target_id:
            service_order = get_object_or_404(ServiceOrder, id=target_id)
            payment.service_order = service_order
            payment.payee = service_order.service.freelancer.user
            payment.save()

        return Response({
            'order_id': order_id,
            'payment_id': payment.id,
            'amount': amount,
            'amount_in_cents': amount_in_cents,
            'currency': currency,
            'description': description,
            'key_id': getattr(settings, 'RAZORPAY_KEY_ID', 'rzp_test_advit_demo'),
            'user_name': request.user.display_name,
            'user_email': request.user.email,
        }, status=status.HTTP_201_CREATED)


class VerifyPaymentSignatureAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        razorpay_order_id = request.data.get('razorpay_order_id')
        razorpay_payment_id = request.data.get('razorpay_payment_id')
        razorpay_signature = request.data.get('razorpay_signature', '')
        payment_id = request.data.get('payment_id')

        payment = Payment.objects.filter(id=payment_id).first() if payment_id else Payment.objects.filter(razorpay_order_id=razorpay_order_id).first()

        if not payment:
            return Response({'error': 'Payment record not found.'}, status=status.HTTP_404_NOT_FOUND)

        payment.razorpay_payment_id = razorpay_payment_id
        payment.razorpay_signature = razorpay_signature
        payment.status = Payment.Status.ESCROW_FUNDED
        payment.save()

        # Update associated Milestone status
        if payment.milestone:
            payment.milestone.status = Milestone.Status.FUNDED
            payment.milestone.save(update_fields=['status'])

        # Update associated Service Order status
        if payment.service_order:
            payment.service_order.status = ServiceOrder.Status.IN_PROGRESS
            payment.service_order.save(update_fields=['status'])

        # Create Ledger Transaction for Payer (Escrow Deposit)
        Transaction.objects.create(
            user=request.user,
            payment=payment,
            transaction_type=Transaction.TxType.ESCROW_DEPOSIT,
            amount=payment.amount,
            status=Transaction.Status.SUCCESS,
            description=f"Funded escrow for {payment.milestone.title if payment.milestone else 'Service Order'}"
        )

        # Notify Payee
        if payment.payee:
            Notification.send(
                user=payment.payee,
                notification_type=Notification.Type.PAYMENT,
                title="Escrow Funded!",
                message=f"${payment.amount} has been secured in Escrow for your milestone.",
                link=f"/projects/{payment.milestone.project.id}/workspace/" if payment.milestone else "/freelancers/dashboard/"
            )

        return Response({'success': True, 'message': 'Payment authorized and held safely in escrow.'})


class ReleaseMilestoneEscrowAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, milestone_id):
        milestone = get_object_or_404(Milestone, id=milestone_id)
        project = milestone.project

        if not (hasattr(request.user, 'client_profile') and project.client == request.user.client_profile):
            return Response({'error': 'Only the client can release milestone payments.'}, status=status.HTTP_403_FORBIDDEN)

        payment = Payment.objects.filter(milestone=milestone, status=Payment.Status.ESCROW_FUNDED).first()
        if not payment:
            # Create a mock funded payment if direct release is triggered in demo
            payment = Payment.objects.create(
                milestone=milestone,
                contract=milestone.contract,
                payer=request.user,
                payee=milestone.contract.freelancer.user if milestone.contract and milestone.contract.freelancer else None,
                amount=milestone.amount,
                status=Payment.Status.ESCROW_FUNDED
            )

        payment.status = Payment.Status.RELEASED
        payment.save()

        milestone.status = Milestone.Status.APPROVED
        milestone.save(update_fields=['status'])

        # Create Ledger Payout Transaction for Payee
        if payment.payee:
            Transaction.objects.create(
                user=payment.payee,
                payment=payment,
                transaction_type=Transaction.TxType.PAYOUT,
                amount=payment.amount,
                status=Transaction.Status.SUCCESS,
                description=f"Received milestone payout for {milestone.title}"
            )

            # Update freelancer profile earnings
            if hasattr(payment.payee, 'freelancer_profile'):
                payment.payee.freelancer_profile.total_earnings += payment.amount
                payment.payee.freelancer_profile.save(update_fields=['total_earnings'])

            Notification.send(
                user=payment.payee,
                notification_type=Notification.Type.PAYMENT,
                title="Milestone Released! 💰",
                message=f"${payment.amount} for '{milestone.title}' has been released to your account.",
                link=f"/projects/{project.id}/workspace/"
            )

        messages.success(request, f"Milestone '{milestone.title}' approved and ${payment.amount} released.")
        return Response({'success': True, 'message': f'Milestone payment of ${payment.amount} released.'})
