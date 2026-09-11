from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, User

from .models import Customer, KeywordMetric, Lead, License, MediaAsset, Partner, Product, SiteSection


class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ("name", "phone")
        error_messages = {
            "name": {"required": "يرجى إدخال الاسم الكامل."},
            "phone": {"required": "يرجى إدخال رقم الموبايل."},
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "اكتب اسمك", "autocomplete": "name"}),
            "phone": forms.TextInput(attrs={"placeholder": "09xx xxx xxx", "autocomplete": "tel", "inputmode": "tel"}),
        }

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if not name:
            raise forms.ValidationError("يرجى إدخال الاسم الكامل.")
        return name

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        if not phone:
            raise forms.ValidationError("يرجى إدخال رقم الموبايل.")
        return phone


class SignUpForm(UserCreationForm):
    username = forms.CharField(
        label="اسم المستخدم",
        max_length=150,
        widget=forms.TextInput(attrs={"autocomplete": "username", "placeholder": "مثال: kajo_user"}),
    )
    password1 = forms.CharField(
        label="كلمة المرور",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", "placeholder": "••••••••"}),
    )
    password2 = forms.CharField(
        label="تأكيد كلمة المرور",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", "placeholder": "••••••••"}),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username",)
        error_messages = {
            "username": {"unique": "اسم المستخدم هذا مستخدم بالفعل. اختر اسماً آخر."},
        }


class ControlModelForm(forms.ModelForm):
    """Shared styling and accessible defaults for the custom control center."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs["class"] = "control-checkbox"
            elif isinstance(widget, forms.SelectMultiple):
                widget.attrs["class"] = "control-input control-multiselect"
            else:
                widget.attrs["class"] = "control-input"
            if isinstance(widget, forms.Textarea):
                widget.attrs.setdefault("rows", 5)


class ProductControlForm(ControlModelForm):
    class Meta:
        model = Product
        fields = "__all__"
        widgets = {"accent": forms.TextInput(attrs={"type": "color"})}


class CustomerControlForm(ControlModelForm):
    class Meta:
        model = Customer
        fields = "__all__"
        widgets = {"phone": forms.TextInput(attrs={"inputmode": "tel", "autocomplete": "tel"})}


class LicenseControlForm(ControlModelForm):
    class Meta:
        model = License
        fields = "__all__"
        widgets = {"expires_at": forms.DateInput(attrs={"type": "date"})}


class PartnerControlForm(ControlModelForm):
    class Meta:
        model = Partner
        fields = "__all__"
        widgets = {"commission_rate": forms.NumberInput(attrs={"min": "0", "max": "100", "step": "0.01"})}


class LeadControlForm(ControlModelForm):
    class Meta:
        model = Lead
        fields = "__all__"
        widgets = {"phone": forms.TextInput(attrs={"inputmode": "tel", "autocomplete": "tel"})}


class MediaAssetControlForm(ControlModelForm):
    class Meta:
        model = MediaAsset
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get("file") and not cleaned_data.get("file_url"):
            self.add_error("file", "ارفع ملفاً أو أضف رابطاً للملف.")
            self.add_error("file_url", "ارفع ملفاً أو أضف رابطاً للملف.")
        return cleaned_data


class SiteSectionControlForm(ControlModelForm):
    class Meta:
        model = SiteSection
        fields = "__all__"


class KeywordMetricControlForm(ControlModelForm):
    class Meta:
        model = KeywordMetric
        fields = "__all__"


class UserControlForm(ControlModelForm):
    password = forms.CharField(
        label="كلمة المرور",
        required=False,
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text="اتركها فارغة عند التعديل للاحتفاظ بكلمة المرور الحالية.",
    )

    class Meta:
        model = User
        fields = (
            "username", "password", "first_name", "last_name", "email",
            "is_active", "is_staff", "is_superuser", "groups",
        )
        widgets = {"email": forms.EmailInput(attrs={"autocomplete": "email"})}

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if not self.instance.pk and not password:
            raise forms.ValidationError("كلمة المرور مطلوبة عند إنشاء مستخدم جديد.")
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if commit:
            user.save()
            self.save_m2m()
        return user


class GroupControlForm(ControlModelForm):
    class Meta:
        model = Group
        fields = ("name", "permissions")
