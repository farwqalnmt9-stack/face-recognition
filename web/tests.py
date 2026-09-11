from django.contrib.auth import get_user_model
from django.conf import settings
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

    def test_favicon_is_available(self):
        response = self.client.get("/favicon.ico")
        self.assertRedirects(
            response,
            f"/static/web/favicon.svg?v={settings.STATIC_VERSION}",
            status_code=301,
            fetch_redirect_response=False,
        )

    def test_demo_request_creates_lead(self):
        response = self.client.post(reverse("home"), {"name": "عميل تجريبي", "phone": "0999999999"})
        self.assertRedirects(response, reverse("home"))
        self.assertTrue(Lead.objects.filter(phone="0999999999").exists())

    def test_invalid_demo_request_renders_errors_without_creating_lead(self):
        response = self.client.post(reverse("home"), {"name": "", "phone": ""})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "يرجى إدخال الاسم الكامل.")
        self.assertContains(response, "يرجى إدخال رقم الموبايل.")
        self.assertEqual(Lead.objects.count(), 0)

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

    def test_navbar_contains_the_control_panel_entry(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, reverse("control_panel"))

    def test_django_admin_root_ui_is_removed_from_rendered_pages(self):
        for route in (
            reverse("home"),
            reverse("products"),
            reverse("product_detail", args=[self.product.slug]),
        ):
            response = self.client.get(route)
            self.assertNotContains(response, 'href="/admin/"')
            self.assertNotContains(response, "إدارة Django")

        home = self.client.get(reverse("home"))
        self.assertNotContains(home, 'id="adminPanel"')
        self.assertNotContains(home, 'href="#"')

        user = get_user_model().objects.create_user("admin_ui_staff", password="test-pass", is_staff=True)
        self.client.force_login(user)
        control = self.client.get(reverse("control_panel"))
        self.assertNotContains(control, 'href="/admin/"')
        self.assertNotContains(control, "إدارة Django")

    def test_django_admin_index_redirects_to_control_panel(self):
        response = self.client.get("/admin/")
        self.assertRedirects(response, reverse("control_panel"), fetch_redirect_response=False)

    def test_django_admin_model_pages_are_no_longer_exposed(self):
        response = self.client.get("/admin/web/sitesection/")
        self.assertEqual(response.status_code, 404)

    def test_custom_control_center_renders_all_business_resources(self):
        staff = get_user_model().objects.create_user("resource_staff", password="test-pass", is_staff=True)
        self.client.force_login(staff)

        for resource_key in ("sections", "media", "products", "leads", "customers", "licenses", "partners", "keywords"):
            list_response = self.client.get(reverse("control_resource_list", args=[resource_key]))
            create_response = self.client.get(reverse("control_resource_create", args=[resource_key]))
            self.assertEqual(list_response.status_code, 200, resource_key)
            self.assertEqual(create_response.status_code, 200, resource_key)
            self.assertNotContains(list_response, "/admin/")

    def test_user_and_group_management_are_limited_to_superusers(self):
        staff = get_user_model().objects.create_user("limited_staff", password="test-pass", is_staff=True)
        self.client.force_login(staff)
        self.assertEqual(self.client.get(reverse("control_resource_list", args=["users"])).status_code, 403)
        self.assertEqual(self.client.get(reverse("control_resource_list", args=["groups"])).status_code, 403)

        superuser = get_user_model().objects.create_superuser("control_superuser", password="test-pass")
        self.client.force_login(superuser)
        self.assertEqual(self.client.get(reverse("control_resource_list", args=["users"])).status_code, 200)
        self.assertEqual(self.client.get(reverse("control_resource_list", args=["groups"])).status_code, 200)

    def test_custom_control_product_crud(self):
        staff = get_user_model().objects.create_user("crud_staff", password="test-pass", is_staff=True)
        self.client.force_login(staff)
        create_url = reverse("control_resource_create", args=["products"])

        response = self.client.post(create_url, {
            "slug": "custom-control-product",
            "name_ar": "منتج من لوحة كاجو",
            "name_en": "Kajo control product",
            "summary_ar": "وصف عربي",
            "summary_en": "English summary",
            "category": "Business software",
            "accent": "#1ca84b",
            "is_active": "on",
        })
        product = Product.objects.get(slug="custom-control-product")
        self.assertRedirects(response, reverse("control_resource_list", args=["products"]))

        edit_url = reverse("control_resource_edit", args=["products", product.pk])
        response = self.client.post(edit_url, {
            "slug": product.slug,
            "name_ar": "منتج معدل",
            "name_en": product.name_en,
            "summary_ar": product.summary_ar,
            "summary_en": product.summary_en,
            "category": product.category,
            "accent": product.accent,
            "is_active": "on",
        })
        self.assertRedirects(response, reverse("control_resource_list", args=["products"]))
        product.refresh_from_db()
        self.assertEqual(product.name_ar, "منتج معدل")

        delete_url = reverse("control_resource_delete", args=["products", product.pk])
        self.assertEqual(self.client.get(delete_url).status_code, 200)
        self.assertRedirects(self.client.post(delete_url), reverse("control_resource_list", args=["products"]))
        self.assertFalse(Product.objects.filter(pk=product.pk).exists())

    def test_signup_creates_a_non_staff_account(self):
        response = self.client.post(reverse("signup"), {
            "username": "new_customer",
            "password1": "SecureKajoPass2026!",
            "password2": "SecureKajoPass2026!",
        })
        self.assertRedirects(response, f'{reverse("login")}?reauth=1')
        user = get_user_model().objects.get(username="new_customer")
        self.assertFalse(user.is_staff)
        self.assertTrue(self.client.login(username="new_customer", password="SecureKajoPass2026!"))

    def test_staff_can_open_signup_without_being_sent_to_control_panel(self):
        staff = get_user_model().objects.create_user(
            "signup_staff",
            password="test-pass",
            is_staff=True,
        )
        self.client.force_login(staff)

        response = self.client.get(reverse("signup"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "أنشئ حسابك")
        self.assertContains(response, f'href="{reverse("login")}?reauth=1"')

        login_response = self.client.get(f'{reverse("login")}?reauth=1')
        self.assertEqual(login_response.status_code, 200)
        self.assertContains(login_response, "أهلاً بعودتك")

    def test_staff_signup_returns_to_login_instead_of_control_panel(self):
        staff = get_user_model().objects.create_user(
            "signup_submit_staff",
            password="test-pass",
            is_staff=True,
        )
        self.client.force_login(staff)

        response = self.client.post(reverse("signup"), {
            "username": "created_from_staff_session",
            "password1": "SecureKajoPass2026!",
            "password2": "SecureKajoPass2026!",
        })

        self.assertRedirects(response, f'{reverse("login")}?reauth=1')

    def test_login_rejects_external_next_url(self):
        get_user_model().objects.create_user("safe_user", password="test-pass")
        response = self.client.post(
            f'{reverse("login")}?next=https://example.com',
            {"username": "safe_user", "password": "test-pass"},
        )
        self.assertRedirects(response, reverse("home"))

    def test_staff_login_defaults_to_control_panel(self):
        get_user_model().objects.create_user("staff_login", password="test-pass", is_staff=True)
        response = self.client.post(
            reverse("login"),
            {"username": "staff_login", "password": "test-pass"},
        )
        self.assertRedirects(response, reverse("control_panel"))

    def test_authenticated_user_can_open_the_login_page_explicitly(self):
        user = get_user_model().objects.create_user("reauth_user", password="test-pass")
        self.client.force_login(user)
        response = self.client.get(f'{reverse("login")}?reauth=1')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "أهلاً بعودتك")

    def test_home_uses_the_focused_product_showcase(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "data-product-showcase")
        self.assertContains(response, 'role="tablist"')
        self.assertNotContains(response, 'class="product-grid"')
