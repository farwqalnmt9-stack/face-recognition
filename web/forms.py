from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


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
