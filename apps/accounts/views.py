from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views import View

from .forms import (
    CustomPasswordChangeForm, LoginForm, ProfileForm,
    RoleForm, UserCreateForm, UserEditForm,
)
from .models import AuditLog, Role, User
from .decorators import role_required


# ─────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────

class LoginView(View):
    template_name = "accounts/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("accounts:dashboard_redirect")
        return render(request, self.template_name, {"form": LoginForm()})

    def post(self, request):
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Using the constant for suspended status
            if user.status == User.STATUS_SUSPENDED:
                messages.error(
                    request, "Your account has been suspended. Contact support.")
                return render(request, self.template_name, {"form": form})
            login(request, user)
            if not form.cleaned_data.get("remember_me"):
                request.session.set_expiry(0)
            # Log the action using constant
            AuditLog.objects.create(
                user=user,
                action=AuditLog.ACTION_LOGIN,
                description=f"{user.get_display_name()} logged in.",
                ip_address=request.META.get("REMOTE_ADDR"),
            )
            # Using correct field name 'must_change_password'
            if user.must_change_password:
                messages.warning(
                    request, "Please change your password before continuing.")
                return redirect("accounts:change_password")
            return redirect("accounts:dashboard_redirect")
        return render(request, self.template_name, {"form": form})


class LogoutView(LoginRequiredMixin, View):
    def post(self, request):
        AuditLog.objects.create(
            user=request.user,
            action=AuditLog.ACTION_LOGOUT,
            description=f"{request.user.get_display_name()} logged out.",
            ip_address=request.META.get("REMOTE_ADDR"),
        )
        logout(request)
        return redirect("accounts:login")


class DashboardRedirectView(LoginRequiredMixin, View):
    """Routes user to the correct portal based on role."""

    def get(self, request):
        portal = request.user.portal
        if portal == "super_admin":
            return redirect("accounts:superadmin_dashboard")
        elif portal == "staff":
            return redirect("accounts:staff_dashboard")
        elif portal == "member":
            return redirect("accounts:member_dashboard")
        messages.error(
            request, "No role assigned to your account. Contact an administrator.")
        return redirect("accounts:login")


# ─────────────────────────────────────────────
# DASHBOARDS (stub views — will be filled per module)
# ─────────────────────────────────────────────

@login_required
def superadmin_dashboard(request):
    context = {
        "total_users": User.objects.count(),
        "total_roles": Role.objects.count(),
        "total_members": User.objects.filter(role__slug=User.ROLE_MEMBER).count(),
        "recent_logs": AuditLog.objects.select_related("user").order_by("-timestamp")[:10],
    }
    return render(request, "accounts/superadmin_dashboard.html", context)


@login_required
def staff_dashboard(request):
    return render(request, "accounts/staff_dashboard.html", {})


@login_required
def member_dashboard(request):
    return render(request, "accounts/member_dashboard.html", {})


# ─────────────────────────────────────────────
# PROFILE & PASSWORD
# ─────────────────────────────────────────────

@login_required
def profile_view(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=request.user)
    return render(request, "accounts/profile.html", {"form": form})


@login_required
def change_password_view(request):
    if request.method == "POST":
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            user.must_change_password = False
            user.save(update_fields=["must_change_password"])
            update_session_auth_hash(request, user)
            AuditLog.objects.create(
                user=user,
                action=AuditLog.ACTION_PASSWORD_CHANGE,
                description="User changed their password.",
                ip_address=request.META.get("REMOTE_ADDR"),
            )
            messages.success(request, "Password changed successfully.")
            return redirect("accounts:dashboard_redirect")
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, "accounts/change_password.html", {"form": form})


# ─────────────────────────────────────────────
# USER MANAGEMENT (Admin / SuperAdmin)
# ─────────────────────────────────────────────

@login_required
@role_required("super_admin", "admin")
def user_list_view(request):
    users = User.objects.select_related("role").order_by("-date_joined")
    return render(request, "accounts/user_list.html", {"users": users})


@login_required
@role_required("super_admin", "admin")
def user_create_view(request):
    if request.method == "POST":
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.created_by = request.user
            user.save()
            AuditLog.objects.create(
                user=request.user,
                action=AuditLog.ACTION_CREATE,
                target_model="User",
                target_id=str(user.pk),
                description=f"Created user {user.get_display_name()}.",
                ip_address=request.META.get("REMOTE_ADDR"),
            )
            messages.success(
                request, f"User {user.get_display_name()} created successfully.")
            return redirect("accounts:user_list")
    else:
        form = UserCreateForm()
    return render(request, "accounts/user_form.html", {"form": form, "action": "Create"})


@login_required
@role_required("super_admin", "admin")
def user_edit_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        form = UserEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            AuditLog.objects.create(
                user=request.user,
                action=AuditLog.ACTION_UPDATE,
                target_model="User",
                target_id=str(user.pk),
                description=f"Updated user {user.get_display_name()}.",
                ip_address=request.META.get("REMOTE_ADDR"),
            )
            messages.success(request, "User updated successfully.")
            return redirect("accounts:user_list")
    else:
        form = UserEditForm(instance=user)
    return render(request, "accounts/user_form.html", {"form": form, "action": "Edit", "target_user": user})


@login_required
@role_required("super_admin", "admin")
def user_detail_view(request, pk):
    target_user = get_object_or_404(
        User.objects.select_related("role", "created_by"), pk=pk)
    logs = AuditLog.objects.filter(
        user=target_user).order_by("-timestamp")[:20]
    return render(request, "accounts/user_detail.html", {"target_user": target_user, "logs": logs})

# ─────────────────────────────────────────────
# ROLE MANAGEMENT (SuperAdmin only)
# ─────────────────────────────────────────────


@login_required
@role_required("super_admin")
def role_list_view(request):
    roles = Role.objects.prefetch_related(
        "permissions", "users").order_by("name")
    return render(request, "accounts/role_list.html", {"roles": roles})


@login_required
@role_required("super_admin")
def role_create_view(request):
    if request.method == "POST":
        form = RoleForm(request.POST)
        if form.is_valid():
            role = form.save()
            AuditLog.objects.create(
                user=request.user,
                action=AuditLog.ACTION_CREATE,
                target_model="Role",
                target_id=str(role.pk),
                description=f"Created role '{role.name}'.",
                ip_address=request.META.get("REMOTE_ADDR"),
            )
            messages.success(request, f"Role '{role.name}' created.")
            return redirect("accounts:role_list")
    else:
        form = RoleForm()
    return render(request, "accounts/role_form.html", {"form": form, "action": "Create"})


@login_required
@role_required("super_admin")
def role_edit_view(request, pk):
    role = get_object_or_404(Role, pk=pk)
    if role.is_system_role:
        messages.warning(request, "System roles cannot be edited.")
        return redirect("accounts:role_list")
    if request.method == "POST":
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            messages.success(request, f"Role '{role.name}' updated.")
            return redirect("accounts:role_list")
    else:
        form = RoleForm(instance=role)
    return render(request, "accounts/role_form.html", {"form": form, "action": "Edit", "role": role})


@login_required
@role_required("super_admin")
def role_delete_view(request, pk):
    role = get_object_or_404(Role, pk=pk)
    if role.is_system_role:
        messages.error(request, "System roles cannot be deleted.")
        return redirect("accounts:role_list")
    if request.method == "POST":
        name = role.name
        role.delete()
        messages.success(request, f"Role '{name}' deleted.")
        return redirect("accounts:role_list")
    return render(request, "accounts/role_confirm_delete.html", {"role": role})
