"""
Management command: python manage.py seed_roles
Creates the default system roles and a super admin user.
"""

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.accounts.models import Role, User


SYSTEM_ROLES = [
    {"name": "Super Admin",   "slug": "super_admin",
        "is_staff_role": True,  "is_system_role": True},
    {"name": "Admin",         "slug": "admin",
        "is_staff_role": True,  "is_system_role": True},
    {"name": "Teller",        "slug": "teller",
        "is_staff_role": True,  "is_system_role": True},
    {"name": "Loan Officer",  "slug": "loan_officer",
        "is_staff_role": True,  "is_system_role": True},
    {"name": "Auditor",       "slug": "auditor",
        "is_staff_role": True,  "is_system_role": True},
    {"name": "Manager",       "slug": "manager",
        "is_staff_role": True,  "is_system_role": True},
    {"name": "Member",        "slug": "member",
        "is_staff_role": False, "is_system_role": True},
]


class Command(BaseCommand):
    help = "Seeds default system roles and creates a super admin user."

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding roles...")
        for data in SYSTEM_ROLES:
            role, created = Role.objects.get_or_create(
                slug=data["slug"],
                defaults={
                    "name": data["name"],
                    "is_staff_role": data["is_staff_role"],
                    "is_system_role": data["is_system_role"],
                }
            )
            status = "Created" if created else "Already exists"
            self.stdout.write(f"  {status}: {role.name}")

        # Create super admin user if none exists
        super_admin_role = Role.objects.get(slug="super_admin")
        if not User.objects.filter(role=super_admin_role).exists():
            self.stdout.write("\nCreating default super admin user...")
            user = User.objects.create_superuser(
                email="admin@sacco.local",
                username="superadmin",
                first_name="Super",
                last_name="Admin",
                password="Admin@1234",
            )
            user.role = super_admin_role
            user.status = User.Status.ACTIVE
            user.force_password_change = True
            user.save()
            self.stdout.write(self.style.SUCCESS(
                "\n  Super admin created:\n"
                "  Email:    admin@sacco.local\n"
                "  Password: Admin@1234\n"
                "  ⚠  Change this password immediately after first login!"
            ))
        else:
            self.stdout.write("  Super admin already exists.")

        self.stdout.write(self.style.SUCCESS(
            "\nDone. Roles seeded successfully."))
