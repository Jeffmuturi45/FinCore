from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    # ── Auth ────────────────────────────────────────────────
    path("login/",           views.login_view,           name="login"),
    path("logout/",          views.logout_view,           name="logout"),
    path("dashboard/",       views.dashboard_view,        name="dashboard"),

    # ── Profile ─────────────────────────────────────────────
    path("profile/",         views.profile_view,          name="profile"),
    path("change-password/", views.change_password_view,  name="change_password"),

    # ── User Management ─────────────────────────────────────
    path("users/",                     views.user_list_view,
         name="user_list"),
    path("users/create/",              views.user_create_view,
         name="user_create"),
    path("users/<int:pk>/",
         views.user_detail_view,        name="user_detail"),
    path("users/<int:pk>/edit/",
         views.user_edit_view,          name="user_edit"),
    path("users/<int:pk>/assign-role/",
         views.assign_role_view,        name="assign_role"),
    path("users/<int:pk>/toggle/",
         views.toggle_user_active_view, name="toggle_active"),

    # ── Role Management (SuperAdmin) ────────────────────────
    path("roles/",                  views.role_list_view,   name="role_list"),
    path("roles/create/",           views.role_create_view, name="role_create"),
    path("roles/<int:pk>/edit/",    views.role_edit_view,   name="role_edit"),
    path("roles/<int:pk>/delete/",  views.role_delete_view, name="role_delete"),
]
