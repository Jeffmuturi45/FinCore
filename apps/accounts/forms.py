from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import get_user_model
from django.utils.text import slugify

from .models import Role

User = get_user_model()


# ─────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────
class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "you@example.com",
            "autofocus": True,
        }),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your password",
        }),
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )


# ─────────────────────────────────────────────
# CREATE USER (Staff / Admin use)
# ─────────────────────────────────────────────
class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Set a password"}),
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Repeat password"}),
    )

    class Meta:
        model = User
        fields = [
            "first_name", "last_name", "email",
            "phone_number", "role", "is_active",
            "must_change_password",
        ]
        widgets = {
            "first_name":           forms.TextInput(attrs={"class": "form-control", "placeholder": "First name"}),
            "last_name":            forms.TextInput(attrs={"class": "form-control", "placeholder": "Last name"}),
            "email":                forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email address"}),
            "phone_number":         forms.TextInput(attrs={"class": "form-control", "placeholder": "+254 7XX XXX XXX"}),
            "role":                 forms.Select(attrs={"class": "form-select"}),
            "is_active":            forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "must_change_password": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


# ─────────────────────────────────────────────
# EDIT USER PROFILE
# ─────────────────────────────────────────────
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone_number", "avatar"]
        widgets = {
            "first_name":   forms.TextInput(attrs={"class": "form-control"}),
            "last_name":    forms.TextInput(attrs={"class": "form-control"}),
            "email":        forms.EmailInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "+254 7XX XXX XXX"}),
            "avatar":       forms.FileInput(attrs={"class": "form-control"}),
        }


# ─────────────────────────────────────────────
# ADMIN: ASSIGN ROLE TO USER
# ─────────────────────────────────────────────
class AssignRoleForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["role", "is_active", "is_staff", "must_change_password"]
        widgets = {
            "role":                 forms.Select(attrs={"class": "form-select"}),
            "is_active":            forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_staff":             forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "must_change_password": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


# ─────────────────────────────────────────────
# ROLE MANAGEMENT (SuperAdmin)
# ─────────────────────────────────────────────
class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ["name", "description", "is_active"]
        widgets = {
            "name":        forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Loan Officer"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "What can this role do?"}),
            "is_active":   forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def save(self, commit=True):
        role = super().save(commit=False)
        if not role.slug:
            role.slug = slugify(role.name)
        if commit:
            role.save()
        return role


# ─────────────────────────────────────────────
# CHANGE PASSWORD
# ─────────────────────────────────────────────
class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"