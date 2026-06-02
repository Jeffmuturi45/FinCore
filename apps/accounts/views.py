from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import get_user_model

from .models import Role, AuditLog
from .forms import (
    LoginForm, UserCreationForm, UserUpdateForm,
    AssignRoleForm, RoleForm, CustomPasswordChangeForm,
)

User = get_user_model()


# ── Helpers ─────────────────────────────────────────────────────────────────
def get_client_ip(request):
    x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded:
        return x_forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def is_super_admin(user):
    return user.is_authenticated and user.is_super_admin()


def log_action(user, action, description="", ip=None):
    AuditLog.objects.create(
        user=user, action=action, description=description, ip_address=ip
    )


# ── Auth ─────────────────────────────────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        if not form.cleaned_data.get("remember_me"):
            request.session.set_expiry(0)   # Session ends on browser close
        user.last_login_ip = get_client_ip(request)
        user.save(update_fields=["last_login_ip"])
        login(request, user)
        log_action(user, "LOGIN", ip=get_client_ip(request))

        if user.must_change_password:
            messages.warning(request, "You must change your password before continuing.")
            return redirect("accounts:change_password")

        return redirect("accounts:dashboard")

    return render(request, "accounts/login.html", {"form": form})


@login_required
def logout_view(request):
    log_action(request.user, "LOGOUT", ip=get_client_ip(request))
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("accounts:login")


# ── Dashboard ────────────────────────────────────────────────────────────────
@login_required
def dashboard_view(request):
    return render(request, "accounts/dashboard.html", {"user": request.user})


# ── Profile ──────────────────────────────────────────────────────────────────
@login_required
def profile_view(request):
    form = UserUpdateForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request.user, "PROFILE_UPDATE", ip=get_client_ip(request))
        messages.success(request, "Profile updated successfully.")
        return redirect("accounts:profile")
    return render(request, "accounts/profile.html", {"form": form})


@login_required
def change_password_view(request):
    form = CustomPasswordChangeForm(request.user, request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        user.must_change_password = False
        user.save(update_fields=["must_change_password"])
        update_session_auth_hash(request, user)
        log_action(user, "PASSWORD_CHANGE", ip=get_client_ip(request))
        messages.success(request, "Password changed successfully.")
        return redirect("accounts:dashboard")
    return render(request, "accounts/change_password.html", {"form": form})


# ── User Management (Staff/Admin) ────────────────────────────────────────────
@login_required
def user_list_view(request):
    if not request.user.is_staff_member():
        messages.error(request, "You do not have permission to view this page.")
        return redirect("accounts:dashboard")

    users = User.objects.select_related("role").all().order_by("first_name")
    return render(request, "accounts/user_list.html", {"users": users})


@login_required
def user_create_view(request):
    if not request.user.is_staff_member():
        messages.error(request, "You do not have permission to perform this action.")
        return redirect("accounts:dashboard")

    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        log_action(request.user, "ACCOUNT_CREATED", description=f"Created user {user.email}", ip=get_client_ip(request))
        messages.success(request, f"Account for {user.get_full_name()} created successfully.")
        return redirect("accounts:user_list")

    return render(request, "accounts/user_form.html", {"form": form, "action": "Create"})


@login_required
def user_detail_view(request, pk):
    if not request.user.is_staff_member():
        messages.error(request, "You do not have permission to view this page.")
        return redirect("accounts:dashboard")

    target_user = get_object_or_404(User, pk=pk)
    logs = AuditLog.objects.filter(user=target_user).order_by("-timestamp")[:20]
    return render(request, "accounts/user_detail.html", {"target_user": target_user, "logs": logs})


@login_required
def user_edit_view(request, pk):
    if not request.user.is_staff_member():
        messages.error(request, "You do not have permission to perform this action.")
        return redirect("accounts:dashboard")

    target_user = get_object_or_404(User, pk=pk)
    form = UserUpdateForm(request.POST or None, request.FILES or None, instance=target_user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "User profile updated.")
        return redirect("accounts:user_detail", pk=pk)
    return render(request, "accounts/user_form.html", {"form": form, "action": "Edit", "target_user": target_user})


@login_required
def assign_role_view(request, pk):
    if not request.user.is_super_admin():
        messages.error(request, "Only Super Admins can assign roles.")
        return redirect("accounts:dashboard")

    target_user = get_object_or_404(User, pk=pk)
    form = AssignRoleForm(request.POST or None, instance=target_user)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(
            request.user, "ROLE_ASSIGNED",
            description=f"Assigned role '{target_user.role}' to {target_user.email}",
            ip=get_client_ip(request),
        )
        messages.success(request, f"Role updated for {target_user.get_full_name()}.")
        return redirect("accounts:user_detail", pk=pk)
    return render(request, "accounts/assign_role.html", {"form": form, "target_user": target_user})


@login_required
def toggle_user_active_view(request, pk):
    if not request.user.is_super_admin():
        messages.error(request, "Only Super Admins can activate/deactivate accounts.")
        return redirect("accounts:dashboard")

    target_user = get_object_or_404(User, pk=pk)
    target_user.is_active = not target_user.is_active
    target_user.save(update_fields=["is_active"])
    action = "ACCOUNT_ACTIVATED" if target_user.is_active else "ACCOUNT_DEACTIVATED"
    log_action(request.user, action, description=f"User: {target_user.email}", ip=get_client_ip(request))
    status = "activated" if target_user.is_active else "deactivated"
    messages.success(request, f"Account {status} successfully.")
    return redirect("accounts:user_detail", pk=pk)


# ── Role Management (SuperAdmin only) ────────────────────────────────────────
@login_required
@user_passes_test(is_super_admin, login_url="/accounts/login/")
def role_list_view(request):
    roles = Role.objects.annotate_user_count() if hasattr(Role.objects, "annotate_user_count") else Role.objects.all()
    roles = Role.objects.all().order_by("name")
    return render(request, "accounts/role_list.html", {"roles": roles})


@login_required
@user_passes_test(is_super_admin, login_url="/accounts/login/")
def role_create_view(request):
    form = RoleForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Role created successfully.")
        return redirect("accounts:role_list")
    return render(request, "accounts/role_form.html", {"form": form, "action": "Create"})


@login_required
@user_passes_test(is_super_admin, login_url="/accounts/login/")
def role_edit_view(request, pk):
    role = get_object_or_404(Role, pk=pk)
    form = RoleForm(request.POST or None, instance=role)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Role updated successfully.")
        return redirect("accounts:role_list")
    return render(request, "accounts/role_form.html", {"form": form, "action": "Edit", "role": role})


@login_required
@user_passes_test(is_super_admin, login_url="/accounts/login/")
def role_delete_view(request, pk):
    role = get_object_or_404(Role, pk=pk)
    if request.method == "POST":
        if role.users.exists():
            messages.error(request, "Cannot delete a role that is assigned to users.")
        else:
            role.delete()
            messages.success(request, "Role deleted.")
        return redirect("accounts:role_list")
    return render(request, "accounts/role_confirm_delete.html", {"role": role})