from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render
from .forms import SignUpForm
from .models import Customer, Lead, License, MediaAsset, Partner, Product, SiteSection


def home(request):
    if request.method == "POST":
        Lead.objects.create(name=request.POST["name"], phone=request.POST["phone"])
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
    }
    return render(request, "web/home.html", context)


def products(request):
    return render(request, "web/products.html", {"products": Product.objects.filter(is_active=True)})


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, "web/product_detail.html", {"product": product})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("control_panel" if request.user.is_staff else "home")
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect(request.GET.get("next") or "admin:index")
    login_media = MediaAsset.objects.filter(placement="login_visual", is_active=True).order_by("-updated_at").first()
    return render(request, "web/login.html", {
        "form": form,
        "login_image_url": login_media.source_url if login_media and login_media.source_url else None,
    })


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("control_panel" if request.user.is_staff else "home")
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "تم إنشاء حسابك بنجاح. يمكنك تسجيل الدخول الآن.")
        return redirect("login")
    login_media = MediaAsset.objects.filter(placement="login_visual", is_active=True).order_by("-updated_at").first()
    return render(request, "web/signup.html", {
        "form": form,
        "login_image_url": login_media.source_url if login_media and login_media.source_url else None,
    })


@staff_member_required(login_url="/login/")
def control_panel(request):
    return render(request, "web/control_panel.html", {
        "section_count": SiteSection.objects.count(),
        "media_count": MediaAsset.objects.count(),
        "product_count": Product.objects.count(),
        "lead_count": Lead.objects.count(),
        "customer_count": Customer.objects.count(),
        "license_count": License.objects.count(),
        "partner_count": Partner.objects.count(),
        "recent_sections": SiteSection.objects.order_by("-updated_at")[:5],
        "recent_media": MediaAsset.objects.order_by("-updated_at")[:5],
    })
