from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class AccountsAuthTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_freelancer_registration_and_profile_creation(self):
        url = reverse('accounts:register')
        data = {
            'username': 'test_freelancer',
            'email': 'fl@example.com',
            'first_name': 'Test',
            'last_name': 'Freelancer',
            'role': User.Role.FREELANCER,
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

        user = User.objects.filter(username='test_freelancer').first()
        self.assertIsNotNone(user)
        self.assertTrue(user.is_freelancer)
        self.assertTrue(hasattr(user, 'freelancer_profile'))

    def test_client_registration_and_profile_creation(self):
        url = reverse('accounts:register')
        data = {
            'username': 'test_client',
            'email': 'client@example.com',
            'first_name': 'Test',
            'last_name': 'Client',
            'role': User.Role.CLIENT,
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

        user = User.objects.filter(username='test_client').first()
        self.assertIsNotNone(user)
        self.assertTrue(user.is_client)
        self.assertTrue(hasattr(user, 'client_profile'))

    def test_login_and_role_redirect(self):
        user = User.objects.create_user(username='loginuser', password='Password123!', role=User.Role.CLIENT)
        from clients.models import ClientProfile
        ClientProfile.objects.create(user=user)

        login_url = reverse('accounts:login')
        response = self.client.post(login_url, {'username': 'loginuser', 'password': 'Password123!'})
        self.assertEqual(response.status_code, 302)

        dashboard_redirect = self.client.get(reverse('accounts:dashboard_redirect'))
        self.assertEqual(dashboard_redirect.status_code, 302)
        self.assertIn('/clients/dashboard/', dashboard_redirect.url)
