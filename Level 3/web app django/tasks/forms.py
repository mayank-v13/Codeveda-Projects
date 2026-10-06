from django import forms
from django.db import models
from django.contrib.auth import get_user_model
from .models import Project, Task, Comment

User = get_user_model()


class ProjectForm(forms.ModelForm):
    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select-multiple'})
    )

    class Meta:
        model = Project
        fields = ['name', 'description', 'status', 'color', 'members']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Mobile App Redesign'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4, 'placeholder': 'Describe project goals, scope, and objectives...'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'color': forms.Select(
                choices=[
                    ('indigo', 'Indigo Pulse'),
                    ('purple', 'Violet Glow'),
                    ('cyan', 'Neon Cyan'),
                    ('emerald', 'Emerald Green'),
                    ('amber', 'Solar Amber'),
                    ('rose', 'Rose Flame'),
                ],
                attrs={'class': 'form-select'}
            ),
        }


class TaskForm(forms.ModelForm):
    due_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-input', 'type': 'date'})
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'project', 'assigned_to', 'status', 'priority', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'What needs to be done?'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4, 'placeholder': 'Provide details, context, and criteria...'}),
            'project': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)

        self.fields['assigned_to'].queryset = User.objects.filter(is_active=True).order_by('first_name', 'username')
        projects = Project.objects.filter(
            status__in=[Project.Status.ACTIVE, Project.Status.PLANNING]
        )
        if user and not user.is_manager_role:
            projects = projects.filter(
                models.Q(members=user) | models.Q(created_by=user)
            ).distinct()
        self.fields['project'].queryset = projects

    def clean(self):
        cleaned_data = super().clean()
        project = cleaned_data.get('project')
        assigned_to = cleaned_data.get('assigned_to')

        if project and assigned_to and not (
            project.members.filter(pk=assigned_to.pk).exists()
            or project.created_by_id == assigned_to.pk
        ):
            self.add_error(
                'assigned_to',
                'The assignee must be a member of the selected project.',
            )
        return cleaned_data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-textarea comment-input',
                'rows': 3,
                'placeholder': 'Share progress, attach thoughts or ask questions...',
                'required': 'required'
            })
        }
        labels = {
            'content': ''
        }
