from .models import Role, User
from django.utils.text import slugify
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
)
from django import forms


# ─────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────

class LoginForm(AuthenticationForm):

    username = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={
            "class": "form-control form-control-lg",
            "placeholder": "you@example.com",
            "autofocus": True,
        }),
    )

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control form-control-lg",
            "placeholder": "••••••••",
        }),
    )

    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={"class": "form-check-input"}
        ),
        label="Keep me signed in",
    )


# ─────────────────────────────────────────────
# USER CREATION
# ─────────────────────────────────────────────

class UserCreateForm(forms.ModelForm):

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={"class": "form-control"}
        ),
    )

    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={"class": "form-control"}
        ),
    )

    class Meta:

        model = User

        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "date_of_birth",
            "gender",
            "id_number",
            "avatar",
            "role",
            "status",
            "is_active",
            "is_verified",
            "must_change_password",
        ]

        widgets = {

            "first_name": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "last_name": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "email": forms.EmailInput(attrs={
                "class": "form-control"
            }),

            "phone_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "+254700000000"
            }),

            "date_of_birth": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),

            "gender": forms.Select(attrs={
                "class": "form-select"
            }),

            "id_number": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "avatar": forms.FileInput(attrs={
                "class": "form-control"
            }),

            "role": forms.Select(attrs={
                "class": "form-select"
            }),

            "status": forms.Select(attrs={
                "class": "form-select"
            }),
        }

    def clean_password2(self):

        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")

        if p1 and p2 and p1 != p2:
            raise forms.ValidationError(
                "Passwords do not match."
            )

        validate_password(p1)

        return p2

    def save(self, commit=True):

        user = super().save(commit=False)

        user.set_password(
            self.cleaned_data["password1"]
        )

        if commit:
            user.save()

        return user


# ─────────────────────────────────────────────
# USER EDIT
# ─────────────────────────────────────────────

class UserEditForm(forms.ModelForm):

    class Meta:

        model = User

        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "date_of_birth",
            "gender",
            "id_number",
            "avatar",
            "role",
            "status",
            "is_active",
            "is_verified",
            "must_change_password",
        ]

        widgets = {

            "first_name": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "last_name": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "email": forms.EmailInput(attrs={
                "class": "form-control"
            }),

            "phone_number": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "date_of_birth": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),

            "gender": forms.Select(attrs={
                "class": "form-select"
            }),

            "id_number": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "avatar": forms.FileInput(attrs={
                "class": "form-control"
            }),

            "role": forms.Select(attrs={
                "class": "form-select"
            }),

            "status": forms.Select(attrs={
                "class": "form-select"
            }),
        }


# ─────────────────────────────────────────────
# PROFILE
# ─────────────────────────────────────────────

class ProfileForm(forms.ModelForm):

    class Meta:

        model = User

        fields = [
            "first_name",
            "last_name",
            "phone_number",
            "date_of_birth",
            "gender",
            "avatar",
        ]

        widgets = {

            "first_name": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "last_name": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "phone_number": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "date_of_birth": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),

            "gender": forms.Select(attrs={
                "class": "form-select"
            }),

            "avatar": forms.FileInput(attrs={
                "class": "form-control"
            }),
        }


# ─────────────────────────────────────────────
# PASSWORD CHANGE
# ─────────────────────────────────────────────

class CustomPasswordChangeForm(
    PasswordChangeForm
):

    old_password = forms.CharField(
        label="Current Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control"
        }),
    )

    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control"
        }),
    )

    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control"
        }),
    )


# ─────────────────────────────────────────────
# ROLE MANAGEMENT
# ─────────────────────────────────────────────

class RoleForm(forms.ModelForm):

    class Meta:

        model = Role

        fields = [
            "name",
            "description",
            "is_active",
        ]

        widgets = {

            "name": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3
            }),

            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),
        }

    def save(self, commit=True):

        role = super().save(commit=False)

        role.slug = slugify(role.name)

        if commit:
            role.save()

        return role
