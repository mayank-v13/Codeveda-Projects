import os
import re
from pathlib import Path
from django.conf import settings


def auth_roles_context(request):
    """
    Exposes role information and local dev email preview tokens to templates.
    """
    context = {
        'is_admin': False,
        'is_manager': False,
        'user_role': 'ANONYMOUS',
        'dev_reset_link': None,
    }

    if request.user.is_authenticated:
        context['is_admin'] = request.user.is_admin_role
        context['is_manager'] = request.user.is_manager_role
        context['user_role'] = getattr(request.user, 'role', 'MEMBER')

    # If DEBUG is True, check if any password reset emails were generated in EMAIL_FILE_PATH
    if settings.DEBUG and hasattr(settings, 'EMAIL_FILE_PATH'):
        email_dir = Path(settings.EMAIL_FILE_PATH)
        if email_dir.exists():
            files = sorted(email_dir.glob('*'), key=os.path.getmtime, reverse=True)
            if files:
                try:
                    content = files[0].read_text(encoding='utf-8', errors='ignore')
                    # Find password reset link in the latest email
                    match = re.search(r'http[s]?://[^\s]+/accounts/reset/[^\s]+', content)
                    if match:
                        context['dev_reset_link'] = match.group(0).rstrip('.')
                except Exception:
                    pass

    return context
