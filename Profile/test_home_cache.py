from django.test import Client, TransactionTestCase, override_settings
from django.core.cache import cache
from django.urls import reverse
from unittest.mock import patch

from ai_asistant_with_sina.query_cache import cached_value
from .models import Users


@override_settings(
    QUERY_CACHE_ENABLED=True,
    CACHES={'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'guest-home-cache-tests',
    }},
)
class GuestHomeCacheTests(TransactionTestCase):
    def setUp(self):
        cache.clear()
        self.addCleanup(cache.clear)
        self.url = reverse('home')
        self.user = Users.objects.create_user(username='home-cache-teacher', role='teacher')

    def test_guest_html_is_shared_and_second_request_skips_rendering(self):
        with patch('Profile.views.cached_value', wraps=cached_value) as lookup:
            cold = self.client.get(self.url)
            warm = Client().get(self.url)
        self.assertEqual(cold.status_code, 200)
        self.assertEqual(cold.content, warm.content)
        self.assertTemplateUsed(cold, 'Profile/home.html')
        self.assertTemplateNotUsed(warm, 'Profile/home.html')
        self.assertEqual(lookup.call_args.args[3], 300)
        self.assertIn(f'href="{reverse("login")}"'.encode(), warm.content)
        self.assertNotIn(f'href="{reverse("teacher panel")}"'.encode(), warm.content)
        self.assertFalse(warm.cookies)
        self.assertIn('Cookie', warm.headers['Vary'])

    def test_authenticated_requests_bypass_guest_cache_in_both_directions(self):
        guest = self.client.get(self.url)
        self.client.force_login(self.user)
        with patch('Profile.views.cached_value', wraps=cached_value) as lookup:
            first = self.client.get(self.url)
            second = self.client.get(self.url)
        lookup.assert_not_called()
        self.assertTemplateUsed(first, 'Profile/home.html')
        self.assertTemplateUsed(second, 'Profile/home.html')
        self.assertIn(f'href="{reverse("teacher panel")}"'.encode(), first.content)
        self.assertNotIn(f'href="{reverse("login")}"'.encode(), first.content)
        self.assertIn('Cookie', first.headers['Vary'])
        self.client.logout()
        again = self.client.get(self.url)
        self.assertEqual(again.content, guest.content)
        self.assertTemplateNotUsed(again, 'Profile/home.html')

    def test_authenticated_first_request_never_populates_guest_html(self):
        self.client.force_login(self.user)
        self.client.get(self.url)
        guest = Client().get(self.url)
        self.assertTemplateUsed(guest, 'Profile/home.html')
        self.assertIn(f'href="{reverse("login")}"'.encode(), guest.content)

    @override_settings(QUERY_CACHE_ENABLED=False)
    def test_disabling_cache_renders_each_guest_request(self):
        first = self.client.get(self.url)
        second = self.client.get(self.url)
        self.assertTemplateUsed(first, 'Profile/home.html')
        self.assertTemplateUsed(second, 'Profile/home.html')

    def test_head_uses_guest_cache_without_returning_a_body(self):
        self.client.get(self.url)
        response = self.client.head(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'')
        self.assertTemplateNotUsed(response, 'Profile/home.html')
