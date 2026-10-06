from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Minimum 8 characters...',
            'autocomplete': 'new-password'
        }),
        help_text='Use at least 8 characters with a mix of letters and numbers.'
    )
    confirm_password = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Repeat your password...',
            'autocomplete': 'new-password'
        })
    )
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'title']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. alex_doe'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'alex@company.com'}),
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Alex'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Doe'}),
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Frontend Engineer'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not email:
            raise forms.ValidationError('Email address is required for authentication and notifications.')
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email address already exists.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password:
            if password != confirm_password:
                self.add_error('confirm_password', 'Passwords do not match. Please verify and try again.')
            else:
                validate_password(password)

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        # Public registrations never grant elevated permissions. Administrators
        # assign Manager and Administrator roles from the team console.
        user.role = CustomUser.Role.MEMBER
        user.is_staff = False
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    username_or_email = forms.CharField(
        label='Username or Email',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your username or email...',
            'autocomplete': 'username',
            'autofocus': 'autofocus',
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': '••••••••',
            'autocomplete': 'current-password',
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'})
    )

    def clean(self):
        cleaned_data = super().clean()
        login_input = cleaned_data.get('username_or_email', '').strip()
        password = cleaned_data.get('password')

        if login_input and password:
            # Check if input is email or username
            user = None
            if '@' in login_input:
                try:
                    user_obj = CustomUser.objects.get(email__iexact=login_input)
                    user = authenticate(username=user_obj.username, password=password)
                except CustomUser.DoesNotExist:
                    pass
            else:
                user = authenticate(username=login_input, password=password)

            if user is None:
                raise forms.ValidationError('Invalid username/email or password. Please verify credentials.')
            elif not user.is_active:
                raise forms.ValidationError('This account has been deactivated. Please contact an administrator.')

            cleaned_data['user'] = user

        return cleaned_data


class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'title', 'bio', 'avatar_color']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Senior Product Architect'}),
            'bio': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4, 'placeholder': 'Tell the team about yourself...'}),
            'avatar_color': forms.Select(
                choices=[
                    ('indigo', 'Indigo Glow'),
                    ('purple', 'Violet Pulse'),
                    ('cyan', 'Neon Cyan'),
                    ('emerald', 'Emerald Forest'),
                    ('amber', 'Warm Amber'),
                    ('rose', 'Rose Velvet'),
                ],
                attrs={'class': 'form-select'}
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.get('instance')
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if self.user and CustomUser.objects.filter(email__iexact=email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError('This email address is already claimed by another account.')
        return email


class AdminUserRoleForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['role', 'is_active', 'is_staff']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label='Registered Email Address',
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your registered email address...',
            'autocomplete': 'email',
            'autofocus': 'autofocus',
        })
    )


class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-input'})
