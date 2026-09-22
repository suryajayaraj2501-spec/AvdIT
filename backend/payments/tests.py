from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from clients.models import ClientProfile
from freelancers.models import FreelancerProfile
from projects.models import Project, Milestone
from proposals.models import Contract, Proposal
from payments.models import Payment, Transaction

User = get_user_model()


class PaymentsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.c_user = User.objects.create_user(username='pay_client', password='Pass1234!', role=User.Role.CLIENT)
        self.client_profile = ClientProfile.objects.create(user=self.c_user)

        self.fl_user = User.objects.create_user(username='pay_freelancer', password='Pass1234!', role=User.Role.FREELANCER)
        self.freelancer_profile = FreelancerProfile.objects.create(user=self.fl_user)

        self.project = Project.objects.create(client=self.client_profile, title='Pay Test Project', budget=500)
        self.milestone = Milestone.objects.create(project=self.project, title='Milestone 1', amount=500, status=Milestone.Status.PENDING)

    def test_payment_creation_and_escrow_verification(self):
        self.client.login(username='pay_client', password='Pass1234!')

        # 1. Create order
        create_url = reverse('payments:api_create_order')
        res = self.client.post(create_url, {
            'order_type': 'milestone',
            'target_id': self.milestone.id,
            'amount': 500,
            'description': 'Milestone Escrow Deposit'
        }, content_type='application/json')
        self.assertEqual(res.status_code, 201)
        data = res.json()
        payment_id = data['payment_id']

        # 2. Verify signature & lock in escrow
        verify_url = reverse('payments:api_verify_signature')
        v_res = self.client.post(verify_url, {
            'payment_id': payment_id,
            'razorpay_order_id': data['order_id'],
            'razorpay_payment_id': 'pay_test_123',
            'razorpay_signature': 'sig_test_123'
        }, content_type='application/json')
        self.assertEqual(v_res.status_code, 200)

        # Check Payment & Milestone updated
        payment = Payment.objects.get(id=payment_id)
        self.assertEqual(payment.status, Payment.Status.ESCROW_FUNDED)

        self.milestone.refresh_from_db()
        self.assertEqual(self.milestone.status, Milestone.Status.FUNDED)

        # Check Transaction record
        tx = Transaction.objects.filter(payment=payment).first()
        self.assertIsNotNone(tx)
        self.assertEqual(tx.transaction_type, Transaction.TxType.ESCROW_DEPOSIT)
