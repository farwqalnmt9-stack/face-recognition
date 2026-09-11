from django.conf import settings
from django.conf.urls.static import static
from django.templatetags.static import static as static_url
from django.urls import path
from django.views.generic import RedirectView
from web.views import (
    control_panel,
    control_resource_create,
    control_resource_delete,
    control_resource_edit,
    control_resource_list,
    home,
    login_view,
    product_detail,
    products,
    signup_view,
)

urlpatterns = [
    path("favicon.ico", RedirectView.as_view(url=static_url("web/favicon.svg"), permanent=True)),
    path("admin/", RedirectView.as_view(pattern_name="control_panel", permanent=False)),
    path("login/", login_view, name="login"),
    path("signup/", signup_view, name="signup"),
    path("control/", control_panel, name="control_panel"),
    path("control/<slug:resource_key>/", control_resource_list, name="control_resource_list"),
    path("control/<slug:resource_key>/new/", control_resource_create, name="control_resource_create"),
    path("control/<slug:resource_key>/<int:pk>/edit/", control_resource_edit, name="control_resource_edit"),
    path("control/<slug:resource_key>/<int:pk>/delete/", control_resource_delete, name="control_resource_delete"),
    path("products/", products, name="products"),
    path("products/<slug:slug>/", product_detail, name="product_detail"),
    path("", home, name="home"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
