from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, Permission, PermissionsMixin


class Role(models.Model):
    """
    Dynamic roles managed by Super Admin.
    """

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    is_system_role = models.BooleanField(default=False)
    
    # Add permissions field
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name="roles"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):

        if not email:
            raise ValueError("Email address is required")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    # ─────────────────────────────────────
    # Constants
    # ─────────────────────────────────────
    
    # Gender Constants
    GENDER_MALE = "Male"
    GENDER_FEMALE = "Female"
    
    # Status Constants
    STATUS_ACTIVE = "Active"
    STATUS_SUSPENDED = "Suspended"
    STATUS_PENDING = "Pending"
    
    # Role Slug Constants
    ROLE_SUPER_ADMIN = "super-admin"
    ROLE_ADMIN = "admin"
    ROLE_STAFF = "staff"
    ROLE_MEMBER = "member"

    GENDER_CHOICES = (
        (GENDER_MALE, "Male"),
        (GENDER_FEMALE, "Female"),
    )

    STATUS_CHOICES = (
        (STATUS_ACTIVE, "Active"),
        (STATUS_SUSPENDED, "Suspended"),
        (STATUS_PENDING, "Pending"),
    )

    # ─────────────────────────────────────
    # Basic Details
    # ─────────────────────────────────────

    email = models.EmailField(unique=True)

    first_name = models.CharField(max_length=100)

    last_name = models.CharField(max_length=100)

    id_number = models.CharField(
        max_length=20,
        unique=True
    )

    phone_number = models.CharField(
        max_length=20,
        blank=True
    )

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True
    )

    date_of_birth = models.DateField(
        null=True,
        blank=True
    )

    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True
    )

    # ─────────────────────────────────────
    # Role
    # ─────────────────────────────────────

    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users"
    )

    # ─────────────────────────────────────
    # Status & Permissions
    # ─────────────────────────────────────

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE
    )

    is_active = models.BooleanField(default=True)

    is_staff = models.BooleanField(default=False)

    is_verified = models.BooleanField(default=False)

    must_change_password = models.BooleanField(default=False)

    # ─────────────────────────────────────
    # Tracking
    # ─────────────────────────────────────

    date_joined = models.DateTimeField(default=timezone.now)

    updated_at = models.DateTimeField(auto_now=True)

    last_login_ip = models.GenericIPAddressField(
        null=True,
        blank=True
    )

    created_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_users'
    )

    # ─────────────────────────────────────
    # Authentication
    # ─────────────────────────────────────

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
        "id_number"
    ]

    objects = UserManager()

    class Meta:
        ordering = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.first_name

    def get_display_name(self):
        """Return display name for the user"""
        return self.get_full_name()

    def has_role(self, slug):
        return self.role and self.role.slug == slug

    def is_super_admin(self):
        return self.is_superuser or self.has_role(self.ROLE_SUPER_ADMIN)

    def is_staff_member(self):

        if self.is_superuser:
            return True

        if self.role:
            return self.role.slug != self.ROLE_MEMBER

        return False

    @property
    def portal(self):
        """
        Returns the portal name based on user's role.
        Used for redirecting users to their respective dashboards.
        """
        if self.is_super_admin():
            return "super_admin"
        elif self.has_role(self.ROLE_ADMIN) or self.has_role(self.ROLE_STAFF):
            return "staff"
        elif self.has_role(self.ROLE_MEMBER):
            return "member"
        return None


class AuditLog(models.Model):

    # Action Constants
    ACTION_LOGIN = "LOGIN"
    ACTION_LOGOUT = "LOGOUT"
    ACTION_PASSWORD_CHANGE = "PASSWORD_CHANGE"
    ACTION_PROFILE_UPDATE = "PROFILE_UPDATE"
    ACTION_ROLE_ASSIGNED = "ROLE_ASSIGNED"
    ACTION_ACCOUNT_CREATED = "ACCOUNT_CREATED"
    ACTION_CREATE = "CREATE"
    ACTION_UPDATE = "UPDATE"

    ACTION_CHOICES = (
        (ACTION_LOGIN, "Login"),
        (ACTION_LOGOUT, "Logout"),
        (ACTION_PASSWORD_CHANGE, "Password Change"),
        (ACTION_PROFILE_UPDATE, "Profile Update"),
        (ACTION_ROLE_ASSIGNED, "Role Assigned"),
        (ACTION_ACCOUNT_CREATED, "Account Created"),
        (ACTION_CREATE, "Create"),
        (ACTION_UPDATE, "Update"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="audit_logs"
    )

    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES
    )

    description = models.TextField(blank=True)

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )

    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Optional fields for tracking target objects
    target_model = models.CharField(max_length=100, blank=True, null=True)
    target_id = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.user} - {self.action}"