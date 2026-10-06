import os
import re
from pathlib import Path
from django.conf import settings
from django.contrib import messages
from django.db import models
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import (
    AdminUserRoleForm,
    CustomPasswordResetForm,
    CustomSetPasswordForm,
    UserLoginForm,
    UserProfileUpdateForm,
    UserRegistrationForm
)
from .models import CustomUser


def register_view(request):
    if request.user.is_authenticated:
        return redirect('tasks:dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in right away
            login(request, user)
            messages.success(
                request,
                f"Welcome to TaskFlow, {user.first_name or user.username}! Your account was created with the {user.get_role_display()} role."
            )
            # Create welcome activity log if tasks app is available
            try:
                from tasks.models import ActivityLog
                ActivityLog.objects.create(
                    user=user,
                    action=f"Joined TaskFlow workspace as {user.get_role_display()}"
                )
            except Exception:
                pass
            return redirect('tasks:dashboard')
        else:
            messages.error(request, "Registration failed. Please check the highlighted errors below.")
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('tasks:dashboard')

    redirect_to = request.GET.get('next', 'tasks:dashboard')
    if not url_has_allowed_host_and_scheme(
        redirect_to,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        redirect_to = 'tasks:dashboard'

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            remember_me = form.cleaned_data.get('remember_me', False)
            login(request, user)

            if remember_me:
                # 2 weeks session expiry
                request.session.set_expiry(1209600)
            else:
                # Browser session
                request.session.set_expiry(0)

            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect(redirect_to)
        else:
            messages.error(request, "Authentication failed. Please verify your credentials.")
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {
        'form': form,
        'next': redirect_to
    })


def demo_login_view(request, role_type):
    """
    Convenience view for testing: 1-click login into demo accounts.
    """
    role_map = {
        'admin': 'admin',
        'manager': 'sarah_manager',
        'member': 'alex_dev',
    }
    username = role_map.get(role_type.lower())
    if not username:
        messages.error(request, "Unknown demo role selected.")
        return redirect('accounts:login')

    try:
        user = CustomUser.objects.get(username=username)
        login(request, user)
        messages.info(
            request,
            f"⚡ Quick Demo Login active! You are now browsing as {user.get_role_display()} ({user.username})."
        )
        return redirect('tasks:dashboard')
    except CustomUser.DoesNotExist:
        messages.warning(
            request,
            f"Demo account '{username}' has not been seeded yet. Please run demo data seeding."
        )
        return redirect('accounts:login')


def logout_view(request):
    if request.user.is_authenticated:
        username = request.user.first_name or request.user.username
        logout(request)
        messages.info(request, f"You have been safely signed out. See you next time, {username}!")
    return redirect('accounts:login')


@login_required
def profile_view(request):
    user = request.user
    profile_form = UserProfileUpdateForm(instance=user)
    password_form = PasswordChangeForm(user=user)

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            profile_form = UserProfileUpdateForm(request.POST, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Your profile details have been updated successfully.")
                return redirect('accounts:profile')
            else:
                messages.error(request, "Could not update profile. Please review the errors below.")

        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(user=user, data=request.POST)
            if password_form.is_valid():
                user_obj = password_form.save()
                update_session_auth_hash(request, user_obj)
                messages.success(request, "Your password has been changed securely.")
                return redirect('accounts:profile')
            else:
                messages.error(request, "Password change failed. Please review the requirements below.")

    # Calculate user statistics
    assigned_tasks_count = user.assigned_tasks.count()
    completed_tasks_count = user.assigned_tasks.filter(status='DONE').count()
    created_tasks_count = user.created_tasks.count()

    context = {
        'profile_form': profile_form,
        'password_form': password_form,
        'assigned_tasks_count': assigned_tasks_count,
        'completed_tasks_count': completed_tasks_count,
        'created_tasks_count': created_tasks_count,
    }
    return render(request, 'accounts/profile.html', context)


def is_admin_check(user):
    return user.is_authenticated and user.is_admin_role


@user_passes_test(is_admin_check, login_url='accounts:login')
def admin_users_view(request):
    """
    Role Management Hub: Administrators can view all users, promote/demote roles,
    and activate/deactivate accounts.
    """
    search_query = request.GET.get('q', '').strip()
    role_filter = request.GET.get('role', '')

    users_qs = CustomUser.objects.all().order_by('-date_joined')

    if search_query:
        users_qs = users_qs.filter(
            models.Q(username__icontains=search_query) |
            models.Q(email__icontains=search_query) |
            models.Q(first_name__icontains=search_query) |
            models.Q(last_name__icontains=search_query)
        )

    if role_filter and role_filter in CustomUser.Role.values:
        users_qs = users_qs.filter(role=role_filter)

    if request.method == 'POST' and 'update_user_role' in request.POST:
        target_user_id = request.POST.get('target_user_id')
        new_role = request.POST.get('new_role')
        target_user = get_object_or_404(CustomUser, pk=target_user_id)

        # Prevent admin from locking themselves out of admin status
        if target_user == request.user and new_role != CustomUser.Role.ADMIN:
            messages.error(request, "You cannot demote yourself from the Administrator role.")
        elif new_role in CustomUser.Role.values:
            old_role = target_user.get_role_display()
            target_user.role = new_role
            if new_role == CustomUser.Role.ADMIN:
                target_user.is_staff = True
            target_user.save()
            messages.success(
                request,
                f"Updated {target_user.username}'s role from {old_role} to {target_user.get_role_display()}."
            )
            try:
                from tasks.models import ActivityLog
                ActivityLog.objects.create(
                    user=request.user,
                    action=f"Changed role of user {target_user.username} to {target_user.get_role_display()}"
                )
            except Exception:
                pass
        return redirect('accounts:admin_users')

    if request.method == 'POST' and 'toggle_user_active' in request.POST:
        target_user_id = request.POST.get('target_user_id')
        target_user = get_object_or_404(CustomUser, pk=target_user_id)
        if target_user == request.user:
            messages.error(request, "You cannot deactivate your own administrative account.")
        else:
            target_user.is_active = not target_user.is_active
            target_user.save()
            status_text = "activated" if target_user.is_active else "deactivated"
            messages.info(request, f"Account '{target_user.username}' has been {status_text}.")
        return redirect('accounts:admin_users')

    total_users = CustomUser.objects.count()
    total_admins = CustomUser.objects.filter(role=CustomUser.Role.ADMIN).count()
    total_managers = CustomUser.objects.filter(role=CustomUser.Role.MANAGER).count()
    total_members = CustomUser.objects.filter(role=CustomUser.Role.MEMBER).count()

    context = {
        'users_list': users_qs,
        'search_query': search_query,
        'role_filter': role_filter,
        'total_users': total_users,
        'total_admins': total_admins,
        'total_managers': total_managers,
        'total_members': total_members,
        'roles': CustomUser.Role.choices,
    }
    return render(request, 'accounts/admin_users.html', context)


# Custom Password Reset Views with Styled Templates
class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/emails/password_reset_email.html'
    subject_template_name = 'accounts/emails/password_reset_subject.txt'
    form_class = CustomPasswordResetForm
    success_url = reverse_lazy('accounts:password_reset_done')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy('accounts:password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'


@user_passes_test(is_admin_check, login_url='accounts:login')
def dev_email_inbox_view(request):
    """
    Local Development Email Inbox Viewer for administrators.
    Allows easy verification and 1-click clicking of password reset links
    generated by Django's filebased email backend.
    """
    emails = []
    email_dir = Path(settings.EMAIL_FILE_PATH)
    if email_dir.exists():
        files = sorted(email_dir.glob('*'), key=os.path.getmtime, reverse=True)
        for f in files[:10]:
            try:
                raw = f.read_text(encoding='utf-8', errors='ignore')
                # Parse Subject, To, Date, and reset link
                subject_match = re.search(r'Subject: (.*)', raw)
                to_match = re.search(r'To: (.*)', raw)
                date_match = re.search(r'Date: (.*)', raw)
                link_match = re.search(r'http[s]?://[^\s]+/accounts/reset/[^\s]+', raw)

                emails.append({
                    'filename': f.name,
                    'subject': subject_match.group(1) if subject_match else 'Password Reset Request',
                    'to': to_match.group(1) if to_match else 'recipient',
                    'date': date_match.group(1) if date_match else '',
                    'reset_link': link_match.group(0).rstrip('.') if link_match else None,
                    'raw_content': raw,
                })
            except Exception:
                continue

    return render(request, 'accounts/dev_email_inbox.html', {'emails': emails})
