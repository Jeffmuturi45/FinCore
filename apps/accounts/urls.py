from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    # Auth
    path("login/",    views.LoginView.as_view(),    name="login"),
    path("logout/",   views.LogoutView.as_view(),   name="logout"),
    path("dashboard/", views.DashboardRedirectView.as_view(),
         name="dashboard_redirect"),

    # Portals
    path("portal/superadmin/", views.superadmin_dashboard,
         name="superadmin_dashboard"),
    path("portal/staff/",      views.staff_dashboard,      name="staff_dashboard"),
    path("portal/member/",     views.member_dashboard,     name="member_dashboard"),

    # Profile
    path("profile/",         views.profile_view,         name="profile"),
    path("change-password/", views.change_password_view, name="change_password"),

    # User management
    path("users/",              views.user_list_view,   name="user_list"),
    path("users/create/",       views.user_create_view, name="user_create"),
    path("users/<int:pk>/",     views.user_detail_view, name="user_detail"),
    path("users/<int:pk>/edit/", views.user_edit_view,   name="user_edit"),

    # Role management
    path("roles/",                   views.role_list_view,   name="role_list"),
    path("roles/create/",            views.role_create_view, name="role_create"),
    path("roles/<int:pk>/edit/",     views.role_edit_view,   name="role_edit"),
    path("roles/<int:pk>/delete/",   views.role_delete_view, name="role_delete"),
]
