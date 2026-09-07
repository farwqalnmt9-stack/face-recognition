from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Lead, Product, SiteSection


class PublicPagesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.product = Product.objects.create(
            slug="test-product",
            name_ar="منتج اختباري",
            name_en="Test product",
            summary_ar="وصف اختباري",
            summary_en="Test summary",
        )

    def test_public_routes_render(self):
        self.assertEqual(self.client.get(reverse("home")).status_code, 200)
        self.assertEqual(self.client.get(reverse("products")).status_code, 200)
        self.assertEqual(self.client.get(reverse("product_detail", args=[self.product.slug])).status_code, 200)
        self.assertEqual(self.client.get(reverse("login")).status_code, 200)
        self.assertEqual(self.client.get(reverse("signup")).status_code, 200)

    def test_demo_request_creates_lead(self):
        response = self.client.post(reverse("home"), {"name": "عميل تجريبي", "phone": "0999999999"})
        self.assertRedirects(response, reverse("home"))
        self.assertTrue(Lead.objects.filter(phone="0999999999").exists())

    def test_home_content_is_loaded_from_editable_sections(self):
        section = SiteSection.objects.get(key="home-hero")
        section.title_ar = "عنوان قابل للتعديل"
        section.save()
        response = self.client.get(reverse("home"))
        self.assertContains(response, "عنوان قابل للتعديل")

    def test_control_panel_requires_staff_and_renders_for_staff(self):
        response = self.client.get(reverse("control_panel"))
        self.assertEqual(response.status_code, 302)
        user = get_user_model().objects.create_user("staff", password="test-pass", is_staff=True)
        self.client.force_login(user)
        response = self.client.get(reverse("control_panel"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "أقسام الصفحات")

    def test_navbar_contains_both_admin_entries(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, reverse("control_panel"))
        self.assertContains(response, reverse("admin:index"))

    def test_signup_creates_a_non_staff_account(self):
        response = self.client.post(reverse("signup"), {
            "username": "new_customer",
            "password1": "SecureKajoPass2026!",
            "password2": "SecureKajoPass2026!",
        })
        self.assertRedirects(response, reverse("login"))
        user = get_user_model().objects.get(username="new_customer")
        self.assertFalse(user.is_staff)
        self.assertTrue(self.client.login(username="new_customer", password="SecureKajoPass2026!"))
