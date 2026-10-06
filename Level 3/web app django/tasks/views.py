from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import CommentForm, ProjectForm, TaskForm
from .models import ActivityLog, Comment, Project, Task


def user_can_access_task(user, task):
    """Return whether a user may view a task and its discussion."""
    return user.is_manager_role or (
        task.assigned_to_id == user.pk
        or task.created_by_id == user.pk
        or (task.project_id and task.project.members.filter(pk=user.pk).exists())
    )


def user_can_edit_task(user, task):
    return user.is_manager_role or task.created_by_id == user.pk or task.assigned_to_id == user.pk


def landing_view(request):
    """
    Public landing page showcasing TaskFlow features, role overview, and live demo access.
    """
    if request.user.is_authenticated:
        return redirect('tasks:dashboard')

    total_tasks_done = Task.objects.filter(status=Task.Status.DONE).count()
    total_projects = Project.objects.count()

    context = {
        'total_tasks_done': total_tasks_done,
        'total_projects': total_projects,
    }
    return render(request, 'tasks/landing.html', context)


@login_required
def dashboard_view(request):
    """
    Main dashboard with Kanban board view, filters, search, and activity metrics.
    """
    user = request.user
    search_query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    project_slug = request.GET.get('project', '')
    view_mode = request.GET.get('view', 'kanban')  # kanban or list

    # Base query for tasks: Admin/Manager can see all tasks; Regular Member sees tasks assigned to them, created by them, or in their projects
    if user.is_manager_role:
        tasks_qs = Task.objects.all().select_related('project', 'assigned_to', 'created_by')
    else:
        tasks_qs = Task.objects.filter(
            Q(assigned_to=user) |
            Q(created_by=user) |
            Q(project__members=user)
        ).distinct().select_related('project', 'assigned_to', 'created_by')

    # Apply filters
    if search_query:
        tasks_qs = tasks_qs.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if status_filter and status_filter in Task.Status.values:
        tasks_qs = tasks_qs.filter(status=status_filter)

    if priority_filter and priority_filter in Task.Priority.values:
        tasks_qs = tasks_qs.filter(priority=priority_filter)

    if project_slug:
        tasks_qs = tasks_qs.filter(project__slug=project_slug)

    # Compute high-level dashboard metrics
    today = timezone.now().date()
    total_count = tasks_qs.count()
    completed_count = tasks_qs.filter(status=Task.Status.DONE).count()
    in_progress_count = tasks_qs.filter(status=Task.Status.IN_PROGRESS).count()
    overdue_count = tasks_qs.filter(due_date__lt=today).exclude(status=Task.Status.DONE).count()

    # Organize tasks into Kanban columns
    kanban_columns = {
        'TODO': tasks_qs.filter(status=Task.Status.TODO),
        'IN_PROGRESS': tasks_qs.filter(status=Task.Status.IN_PROGRESS),
        'IN_REVIEW': tasks_qs.filter(status=Task.Status.IN_REVIEW),
        'DONE': tasks_qs.filter(status=Task.Status.DONE),
    }

    # Available projects for filter dropdown
    projects_list = Project.objects.filter(status=Project.Status.ACTIVE)

    # Recent activities
    recent_activities = ActivityLog.objects.select_related('user', 'task', 'project')[:8]

    context = {
        'tasks': tasks_qs,
        'kanban_columns': kanban_columns,
        'total_count': total_count,
        'completed_count': completed_count,
        'in_progress_count': in_progress_count,
        'overdue_count': overdue_count,
        'search_query': search_query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'project_slug': project_slug,
        'view_mode': view_mode,
        'projects_list': projects_list,
        'recent_activities': recent_activities,
        'today': today,
        'priorities': Task.Priority.choices,
        'statuses': Task.Status.choices,
    }
    return render(request, 'tasks/dashboard.html', context)


@login_required
def project_list_view(request):
    user = request.user
    if user.is_manager_role:
        projects = Project.objects.all().prefetch_related('members', 'tasks')
    else:
        projects = Project.objects.filter(
            Q(members=user) | Q(created_by=user)
        ).distinct().prefetch_related('members', 'tasks')

    context = {
        'projects': projects,
    }
    return render(request, 'tasks/project_list.html', context)


@login_required
def project_detail_view(request, slug):
    project = get_object_or_404(
        Project.objects.prefetch_related('members', 'tasks__assigned_to'),
        slug=slug
    )

    # Permission check for members
    if not request.user.is_manager_role:
        if request.user not in project.members.all() and project.created_by != request.user:
            messages.warning(request, "You do not have access to view this private project.")
            return redirect('tasks:project_list')

    tasks = project.tasks.select_related('assigned_to', 'created_by')

    context = {
        'project': project,
        'tasks': tasks,
    }
    return render(request, 'tasks/project_detail.html', context)


@login_required
def project_create_view(request):
    # Only Admin or Manager can create projects
    if not request.user.is_manager_role:
        messages.error(request, "Permission Denied: Only Managers and Administrators can initiate new projects.")
        return redirect('tasks:project_list')

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            form.save_m2m()
            # Ensure creator is in members
            project.members.add(request.user)

            ActivityLog.objects.create(
                user=request.user,
                action=f"Created new project '{project.name}'",
                project=project
            )

            messages.success(request, f"Project '{project.name}' created successfully!")
            return redirect('tasks:project_detail', slug=project.slug)
    else:
        form = ProjectForm()

    return render(request, 'tasks/project_form.html', {'form': form, 'title': 'Create New Project'})


@login_required
def project_update_view(request, slug):
    project = get_object_or_404(Project, slug=slug)

    # Only project creator, manager, or admin can edit
    if not (request.user.is_admin_role or (request.user.is_manager_role and project.created_by == request.user)):
        messages.error(request, "You do not have permission to modify project settings.")
        return redirect('tasks:project_detail', slug=project.slug)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            ActivityLog.objects.create(
                user=request.user,
                action=f"Updated project settings for '{project.name}'",
                project=project
            )
            messages.success(request, f"Project '{project.name}' updated successfully.")
            return redirect('tasks:project_detail', slug=project.slug)
    else:
        form = ProjectForm(instance=project)

    return render(request, 'tasks/project_form.html', {
        'form': form,
        'project': project,
        'title': f"Edit Project: {project.name}"
    })


@login_required
def project_delete_view(request, slug):
    project = get_object_or_404(Project, slug=slug)

    if not (request.user.is_admin_role or (request.user.is_manager_role and project.created_by == request.user)):
        messages.error(request, "Administrator or Project Owner permission required to delete a project.")
        return redirect('tasks:project_detail', slug=project.slug)

    if request.method == 'POST':
        project_name = project.name
        project.delete()
        ActivityLog.objects.create(
            user=request.user,
            action=f"Deleted project '{project_name}'"
        )
        messages.success(request, f"Project '{project_name}' was removed.")
        return redirect('tasks:project_list')

    return render(request, 'tasks/confirm_delete.html', {
        'item_type': 'Project',
        'item_title': project.name,
        'cancel_url': redirect('tasks:project_detail', slug=project.slug).url
    })


@login_required
def task_create_view(request):
    initial_data = {}
    project_slug = request.GET.get('project')
    if project_slug:
        project = Project.objects.filter(slug=project_slug).first()
        if project:
            if request.user.is_manager_role or project.created_by_id == request.user.pk or project.members.filter(pk=request.user.pk).exists():
                initial_data['project'] = project

    if request.method == 'POST':
        form = TaskForm(request.POST, current_user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()

            ActivityLog.objects.create(
                user=request.user,
                action=f"Created task '{task.title}'",
                task=task,
                project=task.project
            )

            messages.success(request, f"Task '{task.title}' created successfully!")
            return redirect('tasks:task_detail', pk=task.pk)
    else:
        form = TaskForm(initial=initial_data, current_user=request.user)

    return render(request, 'tasks/task_form.html', {'form': form, 'title': 'Create New Task'})


@login_required
def task_detail_view(request, pk):
    task = get_object_or_404(
        Task.objects.select_related('project', 'assigned_to', 'created_by').prefetch_related('comments__author'),
        pk=pk
    )

    if not user_can_access_task(request.user, task):
        messages.error(request, "You do not have permission to view this task.")
        return redirect('tasks:dashboard')

    comment_form = CommentForm()

    if request.method == 'POST' and 'add_comment' in request.POST:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.task = task
            comment.author = request.user
            comment.save()

            ActivityLog.objects.create(
                user=request.user,
                action=f"Commented on task '{task.title}'",
                task=task,
                project=task.project
            )

            messages.success(request, "Comment posted successfully.")
            return redirect('tasks:task_detail', pk=task.pk)

    context = {
        'task': task,
        'comment_form': comment_form,
        'comments': task.comments.all(),
        'statuses': Task.Status.choices,
    }
    return render(request, 'tasks/task_detail.html', context)


@login_required
def task_update_view(request, pk):
    task = get_object_or_404(Task, pk=pk)

    # Check permission: Admin, Manager, or task creator/assignee
    if not user_can_edit_task(request.user, task):
        messages.error(request, "You do not have permission to modify this task.")
        return redirect('tasks:task_detail', pk=task.pk)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, current_user=request.user)
        if form.is_valid():
            form.save()
            ActivityLog.objects.create(
                user=request.user,
                action=f"Updated task details for '{task.title}'",
                task=task,
                project=task.project
            )
            messages.success(request, f"Task '{task.title}' updated successfully.")
            return redirect('tasks:task_detail', pk=task.pk)
    else:
        form = TaskForm(instance=task, current_user=request.user)

    return render(request, 'tasks/task_form.html', {
        'form': form,
        'task': task,
        'title': f"Edit Task: {task.title}"
    })


@login_required
def task_delete_view(request, pk):
    task = get_object_or_404(Task, pk=pk)

    can_delete = request.user.is_manager_role or task.created_by_id == request.user.pk
    if not can_delete:
        messages.error(request, "Permission Denied: Only managers or task creators can delete tasks.")
        return redirect('tasks:task_detail', pk=task.pk)

    if request.method == 'POST':
        title = task.title
        task.delete()
        ActivityLog.objects.create(
            user=request.user,
            action=f"Deleted task '{title}'"
        )
        messages.success(request, f"Task '{title}' has been deleted.")
        return redirect('tasks:dashboard')

    return render(request, 'tasks/confirm_delete.html', {
        'item_type': 'Task',
        'item_title': task.title,
        'cancel_url': redirect('tasks:task_detail', pk=task.pk).url
    })


@login_required
def task_quick_status_view(request, pk):
    """
    POST endpoint to instantly update a task's status from Kanban board or detail page.
    """
    if request.method == 'POST':
        task = get_object_or_404(Task, pk=pk)
        if not user_can_edit_task(request.user, task):
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Permission denied.'}, status=403)
            messages.error(request, "You do not have permission to update this task.")
            return redirect('tasks:dashboard')
        new_status = request.POST.get('status')

        if new_status in Task.Status.values:
            old_status = task.get_status_display()
            task.status = new_status
            task.save()

            ActivityLog.objects.create(
                user=request.user,
                action=f"Updated status of '{task.title}' from {old_status} to {task.get_status_display()}",
                task=task,
                project=task.project
            )

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'status': task.status,
                    'status_display': task.get_status_display(),
                    'badge_class': task.status_badge_class
                })

            messages.success(request, f"Task status updated to {task.get_status_display()}.")

        referer = request.META.get('HTTP_REFERER')
        if referer and url_has_allowed_host_and_scheme(
            referer, allowed_hosts={request.get_host()}, require_https=request.is_secure()
        ):
            return redirect(referer)
        return redirect('tasks:dashboard')

    return redirect('tasks:dashboard')


@login_required
def activity_log_view(request):
    activities = ActivityLog.objects.select_related('user', 'task', 'project')
    if not request.user.is_manager_role:
        activities = activities.filter(
            Q(user=request.user)
            | Q(task__assigned_to=request.user)
            | Q(task__created_by=request.user)
            | Q(task__project__members=request.user)
            | Q(project__created_by=request.user)
            | Q(project__members=request.user)
        ).distinct()
    activities = activities[:50]
    return render(request, 'tasks/activity_log.html', {'activities': activities})
