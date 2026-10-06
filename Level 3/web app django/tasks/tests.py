from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser

from .forms import TaskForm
from .models import ActivityLog, Project, Task


class TaskAccessTests(TestCase):
    def setUp(self):
        self.manager = CustomUser.objects.create_user(
            username='manager', password='SecurePass123!', role=CustomUser.Role.MANAGER
        )
        self.member = CustomUser.objects.create_user(
            username='member', password='SecurePass123!', role=CustomUser.Role.MEMBER
        )
        self.outsider = CustomUser.objects.create_user(
            username='outsider', password='SecurePass123!', role=CustomUser.Role.MEMBER
        )
        self.project = Project.objects.create(name='Private Project', created_by=self.manager)
        self.project.members.add(self.manager, self.member)
        self.task = Task.objects.create(
            title='Private task', project=self.project, assigned_to=self.member, created_by=self.manager
        )

    def test_member_cannot_access_another_projects_task(self):
        self.client.force_login(self.outsider)

        response = self.client.get(reverse('tasks:task_detail', args=[self.task.pk]))
        self.assertRedirects(response, reverse('tasks:dashboard'))

        response = self.client.post(
            reverse('tasks:task_status', args=[self.task.pk]), {'status': Task.Status.DONE}
        )
        self.assertRedirects(response, reverse('tasks:dashboard'))
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, Task.Status.TODO)

    def test_member_task_form_only_offers_accessible_projects(self):
        inaccessible_project = Project.objects.create(name='Restricted', created_by=self.manager)

        form = TaskForm(current_user=self.member)

        self.assertIn(self.project, form.fields['project'].queryset)
        self.assertNotIn(inaccessible_project, form.fields['project'].queryset)

    def test_assignee_must_belong_to_project(self):
        form = TaskForm(
            data={
                'title': 'Invalid assignment',
                'project': self.project.pk,
                'assigned_to': self.outsider.pk,
                'status': Task.Status.TODO,
                'priority': Task.Priority.MEDIUM,
            },
            current_user=self.member,
        )

        self.assertFalse(form.is_valid())
        self.assertIn('assigned_to', form.errors)

    def test_project_task_link_prefills_project_from_slug(self):
        self.client.force_login(self.member)

        response = self.client.get(reverse('tasks:task_create'), {'project': self.project.slug})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form'].initial['project'], self.project)

    def test_activity_log_is_limited_to_accessible_work(self):
        other_project = Project.objects.create(name='Other', created_by=self.manager)
        other_task = Task.objects.create(title='Other task', project=other_project, created_by=self.manager)
        visible_activity = ActivityLog.objects.create(user=self.member, action='Visible', task=self.task)
        hidden_activity = ActivityLog.objects.create(user=self.manager, action='Hidden', task=other_task)
        self.client.force_login(self.member)

        response = self.client.get(reverse('tasks:activity_log'))

        self.assertContains(response, visible_activity.action)
        self.assertNotContains(response, hidden_activity.action)

    def test_authenticated_pages_render(self):
        self.client.force_login(self.manager)
        urls = [
            reverse('tasks:dashboard'),
            reverse('tasks:project_list'),
            reverse('tasks:project_detail', args=[self.project.slug]),
            reverse('tasks:project_create'),
            reverse('tasks:project_update', args=[self.project.slug]),
            reverse('tasks:project_delete', args=[self.project.slug]),
            reverse('tasks:task_create'),
            reverse('tasks:task_detail', args=[self.task.pk]),
            reverse('tasks:task_update', args=[self.task.pk]),
            reverse('tasks:task_delete', args=[self.task.pk]),
            reverse('tasks:activity_log'),
            reverse('accounts:profile'),
        ]

        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

# Create your tests here.
