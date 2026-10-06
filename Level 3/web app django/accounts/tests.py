from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from .forms import UserRegistrationForm
from .models import CustomUser


class LoginSecurityTests(TestCase):
    def test_login_rejects_an_external_next_url(self):
        CustomUser.objects.create_user(username='alex', password='SecurePass123!')

        response = self.client.post(
            f"{reverse('accounts:login')}?next=https://example.com",
            {'username_or_email': 'alex', 'password': 'SecurePass123!', 'remember_me': 'on'},
        )

        self.assertRedirects(response, reverse('tasks:dashboard'))

    def test_public_and_administrator_pages_render(self):
        admin = CustomUser.objects.create_user(
            username='admin', password='SecurePass123!', role=CustomUser.Role.ADMIN, is_staff=True
        )
        public_urls = [
            reverse('tasks:landing'),
            reverse('accounts:register'),
            reverse('accounts:login'),
            reverse('accounts:password_reset'),
            reverse('accounts:password_reset_done'),
        ]
        for url in public_urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

        self.client.force_login(admin)
        self.assertEqual(self.client.get(reverse('accounts:admin_users')).status_code, 200)
        self.assertEqual(self.client.get(reverse('accounts:dev_email_inbox')).status_code, 200)

    def test_public_registration_always_creates_a_regular_member(self):
        form = UserRegistrationForm(data={
            'username': 'new_user',
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'title': 'Developer',
            'password': 'SecurePass123!',
            'confirm_password': 'SecurePass123!',
            # A forged role value must not result in elevated access.
            'role': CustomUser.Role.ADMIN,
        })

        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.role, CustomUser.Role.MEMBER)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.check_password('SecurePass123!'))

    def test_password_reset_sends_an_email_for_registered_user(self):
        CustomUser.objects.create_user(
            username='reset_user', email='reset@example.com', password='SecurePass123!'
        )

        with override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
            response = self.client.post(
                reverse('accounts:password_reset'), {'email': 'reset@example.com'}
            )

        self.assertRedirects(response, reverse('accounts:password_reset_done'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('/accounts/reset/', mail.outbox[0].body)

    def test_reset_mailbox_requires_an_administrator(self):
        member = CustomUser.objects.create_user(username='member', password='SecurePass123!')
        self.client.force_login(member)

        response = self.client.get(reverse('accounts:dev_email_inbox'))

        self.assertEqual(response.status_code, 302)

# Create your tests here.
