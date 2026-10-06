from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'role', 'title', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('TaskFlow Permissions & Profile', {'fields': ('role', 'title', 'bio', 'avatar_color')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('TaskFlow Permissions & Profile', {'fields': ('role', 'title', 'bio', 'avatar_color')}),
    )
