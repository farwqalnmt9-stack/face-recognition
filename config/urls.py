from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from web.views import control_panel, home, login_view, product_detail, products, signup_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", login_view, name="login"),
    path("signup/", signup_view, name="signup"),
    path("control/", control_panel, name="control_panel"),
    path("products/", products, name="products"),
    path("products/<slug:slug>/", product_detail, name="product_detail"),
    path("", home, name="home"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
