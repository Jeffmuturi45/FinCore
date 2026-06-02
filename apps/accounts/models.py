from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class Role(models.Model):
    """
    Dynamic roles that SuperAdmin can create and manage.
    e.g. Super Admin, HR Officer, Loan Officer, Teller, Member, Manager
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Role"
        verbose_name_plural = "Roles"

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email address is required.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Central user model. Roles are assigned via Role FK.
    Django groups/permissions work alongside roles for fine-grained access.
    """

    # ── Identity ────────────────────────────────────────────
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    # ── Role ────────────────────────────────────────────────
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )

    # ── Status ──────────────────────────────────────────────
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)       # Django admin access
    is_verified = models.BooleanField(default=False)    # Email / KYC verified
    must_change_password = models.BooleanField(
        default=False)  # Force reset on first login

    # ── Timestamps ──────────────────────────────────────────
    date_joined = models.DateTimeField(default=timezone.now)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        ordering = ["first_name", "last_name"]
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.get_full_name()} <{self.email}>"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name

    # ── Role helpers ────────────────────────────────────────
    def has_role(self, slug):
        """Check if user has a specific role by slug."""
        return self.role is not None and self.role.slug == slug

    def is_super_admin(self):
        return self.is_superuser or self.has_role("super-admin")

    def is_staff_member(self):
        """True for any internal staff (not plain members)."""
        if self.is_superuser:
            return True
        if self.role:
            return self.role.slug not in ("member",)
        return False


class AuditLog(models.Model):
    """Tracks key user account actions for compliance."""

    ACTION_CHOICES = [
        ("LOGIN", "Login"),
        ("LOGOUT", "Logout"),
        ("PASSWORD_CHANGE", "Password Change"),
        ("PASSWORD_RESET", "Password Reset"),
        ("PROFILE_UPDATE", "Profile Update"),
        ("ROLE_ASSIGNED", "Role Assigned"),
        ("ACCOUNT_CREATED", "Account Created"),
        ("ACCOUNT_DEACTIVATED", "Account Deactivated"),
        ("ACCOUNT_ACTIVATED", "Account Activated"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"

    def __str__(self):
        return f"{self.user} — {self.action} @ {self.timestamp:%Y-%m-%d %H:%M}"
