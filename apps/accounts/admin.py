from .models import (
    Role,
    User,
    AuditLog,
)
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin


# ─────────────────────────────────────────────
# ROLE ADMIN
# ─────────────────────────────────────────────

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "slug",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "slug",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }

    ordering = (
        "name",
    )


# ─────────────────────────────────────────────
# USER ADMIN
# ─────────────────────────────────────────────

@admin.register(User)
class UserAdmin(BaseUserAdmin):

    ordering = (
        "date_joined",
    )

    list_display = (
        "email",
        "first_name",
        "last_name",
        "role",
        "status",
        "is_active",
        "is_staff",
        "date_joined",
    )

    list_filter = (
        "is_active",
        "is_staff",
        "is_verified",
        "status",
        "role",
    )

    search_fields = (
        "email",
        "first_name",
        "last_name",
        "id_number",
    )

    readonly_fields = (
        "date_joined",
        "updated_at",
        "last_login",
    )

    fieldsets = (

        ("Authentication", {
            "fields": (
                "email",
                "password",
            )
        }),

        ("Personal Info", {
            "fields": (
                "first_name",
                "last_name",
                "phone_number",
                "id_number",
                "gender",
                "date_of_birth",
                "avatar",
            )
        }),

        ("Role & Permissions", {
            "fields": (
                "role",
                "status",
                "is_active",
                "is_staff",
                "is_superuser",
                "is_verified",
                "must_change_password",
                "groups",
                "user_permissions",
            )
        }),

        ("Tracking", {
            "fields": (
                "date_joined",
                "updated_at",
                "last_login",
                "last_login_ip",
            )
        }),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "id_number",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )


# ─────────────────────────────────────────────
# AUDIT LOG ADMIN
# ─────────────────────────────────────────────

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "action",
        "ip_address",
        "timestamp",
    )

    list_filter = (
        "action",
        "timestamp",
    )

    search_fields = (
        "user__email",
        "description",
        "ip_address",
    )

    readonly_fields = (
        "user",
        "action",
        "description",
        "ip_address",
        "timestamp",
    )

    ordering = (
        "-timestamp",
    )
