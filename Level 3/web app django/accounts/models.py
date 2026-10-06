from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrator'
        MANAGER = 'MANAGER', 'Project Manager'
        MEMBER = 'MEMBER', 'Team Member'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.MEMBER,
        help_text='Designates the role and permission level in TaskFlow.'
    )
    bio = models.TextField(blank=True, default='')
    title = models.CharField(max_length=100, blank=True, default='Team Contributor')
    avatar_color = models.CharField(max_length=30, default='indigo')

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_manager_role(self):
        return self.role in (self.Role.ADMIN, self.Role.MANAGER) or self.is_superuser

    @property
    def role_badge_class(self):
        if self.is_admin_role:
            return 'badge-admin'
        elif self.role == self.Role.MANAGER:
            return 'badge-manager'
        return 'badge-member'

    @property
    def initials(self):
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        return self.username[:2].upper()

    def save(self, *args, **kwargs):
        if self.is_superuser and self.role != self.Role.ADMIN:
            self.role = self.Role.ADMIN
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
