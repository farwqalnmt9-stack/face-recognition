from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group, User
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import (
    CustomerControlForm,
    GroupControlForm,
    KeywordMetricControlForm,
    LeadControlForm,
    LeadForm,
    LicenseControlForm,
    MediaAssetControlForm,
    PartnerControlForm,
    ProductControlForm,
    SignUpForm,
    SiteSectionControlForm,
    UserControlForm,
)
from .models import Customer, KeywordMetric, Lead, License, MediaAsset, Partner, Product, SiteSection


CONTROL_RESOURCES = {
    "sections": {
        "model": SiteSection, "form": SiteSectionControlForm, "label": "أقسام الصفحات",
        "singular": "قسم صفحة", "index": "01", "search": ("title_ar", "title_en", "key", "page"),
        "columns": (("title_ar", "العنوان"), ("page", "الصفحة"), ("key", "المعرّف"), ("order", "الترتيب"), ("is_visible", "ظاهر")),
        "order_by": ("page", "order"),
    },
    "media": {
        "model": MediaAsset, "form": MediaAssetControlForm, "label": "الصور والوسائط",
        "singular": "وسيط", "index": "02", "search": ("title", "alt_text", "file_url"),
        "columns": (("title", "العنوان"), ("type", "النوع"), ("placement", "المكان"), ("product", "المنتج"), ("is_active", "ظاهر")),
        "order_by": ("-updated_at",), "select_related": ("product",),
    },
    "products": {
        "model": Product, "form": ProductControlForm, "label": "المنتجات",
        "singular": "منتج", "index": "03", "search": ("name_ar", "name_en", "slug", "category"),
        "columns": (("name_ar", "الاسم"), ("category", "التصنيف"), ("slug", "الرابط"), ("is_active", "نشط")),
        "order_by": ("name_ar",),
    },
    "leads": {
        "model": Lead, "form": LeadControlForm, "label": "فرص البيع",
        "singular": "فرصة بيع", "index": "04", "search": ("name", "phone", "notes"),
        "columns": (("name", "الاسم"), ("phone", "الهاتف"), ("stage", "المرحلة"), ("created_at", "تاريخ الطلب")),
        "order_by": ("-created_at",),
    },
    "customers": {
        "model": Customer, "form": CustomerControlForm, "label": "العملاء",
        "singular": "عميل", "index": "05", "search": ("name", "contact_name", "phone", "city"),
        "columns": (("name", "الاسم"), ("contact_name", "جهة الاتصال"), ("phone", "الهاتف"), ("city", "المدينة")),
        "order_by": ("-updated_at",),
    },
    "licenses": {
        "model": License, "form": LicenseControlForm, "label": "التراخيص",
        "singular": "ترخيص", "index": "06", "search": ("key", "customer__name", "product__name_ar"),
        "columns": (("key", "المفتاح"), ("product", "المنتج"), ("customer", "العميل"), ("status", "الحالة"), ("expires_at", "الانتهاء")),
        "order_by": ("-updated_at",), "select_related": ("product", "customer"),
    },
    "partners": {
        "model": Partner, "form": PartnerControlForm, "label": "الوكلاء",
        "singular": "وكيل", "index": "07", "search": ("name", "region"),
        "columns": (("name", "الاسم"), ("region", "المنطقة"), ("commission_rate", "العمولة %"), ("is_active", "نشط")),
        "order_by": ("name",),
    },
    "keywords": {
        "model": KeywordMetric, "form": KeywordMetricControlForm, "label": "الكلمات المفتاحية",
        "singular": "كلمة مفتاحية", "index": "08", "search": ("keyword",),
        "columns": (("keyword", "الكلمة"), ("monthly_volume", "حجم البحث"), ("difficulty", "الصعوبة"), ("rank", "الترتيب")),
        "order_by": ("-monthly_volume",),
    },
    "users": {
        "model": User, "form": UserControlForm, "label": "المستخدمون",
        "singular": "مستخدم", "index": "09", "search": ("username", "first_name", "last_name", "email"),
        "columns": (("username", "اسم المستخدم"), ("email", "البريد"), ("is_staff", "إدارة"), ("is_active", "نشط")),
        "order_by": ("username",), "superuser_only": True,
    },
    "groups": {
        "model": Group, "form": GroupControlForm, "label": "المجموعات والصلاحيات",
        "singular": "مجموعة", "index": "10", "search": ("name",),
        "columns": (("name", "اسم المجموعة"),), "order_by": ("name",), "superuser_only": True,
    },
}


def _available_resources(user):
    return [
        {"key": key, **resource, "count": resource["model"].objects.count()}
        for key, resource in CONTROL_RESOURCES.items()
        if not resource.get("superuser_only") or user.is_superuser
    ]


def _control_context(request, **extra):
    context = {"control_resources": _available_resources(request.user)}
    context.update(extra)
    return context


def _get_control_resource(request, resource_key):
    try:
        resource = CONTROL_RESOURCES[resource_key]
    except KeyError as exc:
        raise Http404("قسم الإدارة غير موجود") from exc
    if resource.get("superuser_only") and not request.user.is_superuser:
        raise PermissionDenied
    return resource


def _display_value(instance, field_name):
    display_method = getattr(instance, f"get_{field_name}_display", None)
    value = display_method() if display_method else getattr(instance, field_name)
    if value is True:
        return "نعم", True
    if value is False:
        return "لا", True
    if value in (None, ""):
        return "—", False
    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d"), False
    return str(value), False


def home(request):
    lead_form = LeadForm(request.POST or None)
    if request.method == "POST" and lead_form.is_valid():
        lead_form.save()
        messages.success(request, "تم استلام طلبك. سيتواصل معك فريق كاجو قريباً.")
        return redirect("home")
    section_map = {section.key: section for section in SiteSection.objects.filter(page="home")}
    hero_media = MediaAsset.objects.filter(placement="home_hero", is_active=True).order_by("-updated_at").first()
    success_media = MediaAsset.objects.filter(placement="home_success", is_active=True).order_by("-updated_at").first()
    context = {
        "products": Product.objects.filter(is_active=True),
        "hero_section": section_map.get("home-hero"),
        "solutions_section": section_map.get("home-solutions"),
        "products_section": section_map.get("home-products"),
        "control_section": section_map.get("home-control"),
        "success_section": section_map.get("home-success"),
        "partners_section": section_map.get("home-partners"),
        "demo_section": section_map.get("home-demo"),
        "hero_image_url": hero_media.source_url if hero_media and hero_media.source_url else None,
        "success_image_url": success_media.source_url if success_media and success_media.source_url else None,
        "lead_form": lead_form,
    }
    return render(request, "web/home.html", context)


def products(request):
    return render(request, "web/products.html", {"products": Product.objects.filter(is_active=True)})


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, "web/product_detail.html", {"product": product})


def login_view(request):
    if request.user.is_authenticated and request.GET.get("reauth") != "1":
        return redirect("control_panel" if request.user.is_staff else "home")
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        next_url = request.GET.get("next")
        if next_url and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return redirect(next_url)
        return redirect("control_panel" if user.is_staff else "home")
    login_media = MediaAsset.objects.filter(placement="login_visual", is_active=True).order_by("-updated_at").first()
    return render(request, "web/login.html", {
        "form": form,
        "login_image_url": login_media.source_url if login_media and login_media.source_url else None,
    })


def signup_view(request):
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "تم إنشاء حسابك بنجاح. يمكنك تسجيل الدخول الآن.")
        return redirect(f"{reverse('login')}?reauth=1")
    login_media = MediaAsset.objects.filter(placement="login_visual", is_active=True).order_by("-updated_at").first()
    return render(request, "web/signup.html", {
        "form": form,
        "login_image_url": login_media.source_url if login_media and login_media.source_url else None,
    })


@staff_member_required(login_url="/login/")
def control_panel(request):
    return render(request, "web/control_panel.html", _control_context(request,
        active_resource="dashboard",
        section_count=SiteSection.objects.count(),
        media_count=MediaAsset.objects.count(),
        product_count=Product.objects.count(),
        lead_count=Lead.objects.count(),
        customer_count=Customer.objects.count(),
        license_count=License.objects.count(),
        partner_count=Partner.objects.count(),
        recent_sections=SiteSection.objects.order_by("-updated_at")[:5],
        recent_media=MediaAsset.objects.order_by("-updated_at")[:5],
    ))


@staff_member_required(login_url="/login/")
def control_resource_list(request, resource_key):
    resource = _get_control_resource(request, resource_key)
    queryset = resource["model"].objects.all()
    if resource.get("select_related"):
        queryset = queryset.select_related(*resource["select_related"])

    query = request.GET.get("q", "").strip()
    if query:
        search_query = Q()
        for field_name in resource["search"]:
            search_query |= Q(**{f"{field_name}__icontains": query})
        queryset = queryset.filter(search_query)
    queryset = queryset.order_by(*resource["order_by"])

    page = Paginator(queryset, 20).get_page(request.GET.get("page"))
    rows = []
    for instance in page.object_list:
        values = []
        for field_name, _ in resource["columns"]:
            value, is_boolean = _display_value(instance, field_name)
            values.append({"value": value, "is_boolean": is_boolean, "truthy": value == "نعم"})
        rows.append({"instance": instance, "values": values})

    return render(request, "web/control_resource_list.html", _control_context(request,
        active_resource=resource_key,
        resource_key=resource_key,
        resource=resource,
        page=page,
        rows=rows,
        query=query,
    ))


@staff_member_required(login_url="/login/")
def control_resource_create(request, resource_key):
    resource = _get_control_resource(request, resource_key)
    form = resource["form"](request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        instance = form.save()
        messages.success(request, f"تمت إضافة {resource['singular']} «{instance}» بنجاح.")
        return redirect("control_resource_list", resource_key=resource_key)
    return render(request, "web/control_resource_form.html", _control_context(request,
        active_resource=resource_key,
        resource_key=resource_key,
        resource=resource,
        form=form,
        is_create=True,
    ))


@staff_member_required(login_url="/login/")
def control_resource_edit(request, resource_key, pk):
    resource = _get_control_resource(request, resource_key)
    instance = get_object_or_404(resource["model"], pk=pk)
    form = resource["form"](request.POST or None, request.FILES or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        instance = form.save()
        messages.success(request, f"تم حفظ تعديلات «{instance}».")
        return redirect("control_resource_list", resource_key=resource_key)
    return render(request, "web/control_resource_form.html", _control_context(request,
        active_resource=resource_key,
        resource_key=resource_key,
        resource=resource,
        form=form,
        instance=instance,
        is_create=False,
    ))


@staff_member_required(login_url="/login/")
def control_resource_delete(request, resource_key, pk):
    resource = _get_control_resource(request, resource_key)
    instance = get_object_or_404(resource["model"], pk=pk)
    if resource["model"] is User and instance.pk == request.user.pk:
        messages.error(request, "لا يمكنك حذف الحساب الذي تستخدمه حالياً.")
        return redirect("control_resource_list", resource_key=resource_key)
    if request.method == "POST":
        label = str(instance)
        try:
            instance.delete()
        except ProtectedError:
            messages.error(request, "لا يمكن حذف هذا السجل لأنه مرتبط بسجلات أخرى.")
        else:
            messages.success(request, f"تم حذف «{label}».")
        return redirect("control_resource_list", resource_key=resource_key)
    return render(request, "web/control_resource_delete.html", _control_context(request,
        active_resource=resource_key,
        resource_key=resource_key,
        resource=resource,
        instance=instance,
    ))
