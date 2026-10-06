from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import CustomUser
from tasks.models import ActivityLog, Comment, Project, Task


class Command(BaseCommand):
    help = 'Seeds TaskFlow database with demo users, roles, projects, tasks, comments, and activities.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Seeding TaskFlow demo dataset...'))

        today = timezone.now().date()

        # 1. Create or update Demo Users
        admin_user, created = CustomUser.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@taskflow.dev',
                'first_name': 'Mayank',
                'last_name': 'Verma',
                'role': CustomUser.Role.ADMIN,
                'title': 'Head of Engineering & Security',
                'bio': 'Oversees engineering infrastructure, cloud security, user permissions and release cycles.',
                'avatar_color': 'indigo',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin_user.set_password('AdminPass123!')
        admin_user.role = CustomUser.Role.ADMIN
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()

        manager_user, created = CustomUser.objects.get_or_create(
            username='sarah_manager',
            defaults={
                'email': 'sarah@taskflow.dev',
                'first_name': 'Sarah',
                'last_name': 'Jenkins',
                'role': CustomUser.Role.MANAGER,
                'title': 'Lead Technical Product Manager',
                'bio': 'Directs cross-functional sprint planning, roadmap execution, and team resource allocation.',
                'avatar_color': 'purple',
                'is_staff': False,
                'is_superuser': False,
            }
        )
        manager_user.set_password('ManagerPass123!')
        manager_user.role = CustomUser.Role.MANAGER
        manager_user.save()

        alex_user, created = CustomUser.objects.get_or_create(
            username='alex_dev',
            defaults={
                'email': 'alex@taskflow.dev',
                'first_name': 'Alex',
                'last_name': 'Chen',
                'role': CustomUser.Role.MEMBER,
                'title': 'Senior Full-Stack Engineer',
                'bio': 'Specializes in high-performance web systems, Django backend architecture, and reactive UI.',
                'avatar_color': 'cyan',
                'is_staff': False,
                'is_superuser': False,
            }
        )
        alex_user.set_password('MemberPass123!')
        alex_user.role = CustomUser.Role.MEMBER
        alex_user.save()

        elena_user, created = CustomUser.objects.get_or_create(
            username='elena_designer',
            defaults={
                'email': 'elena@taskflow.dev',
                'first_name': 'Elena',
                'last_name': 'Rostova',
                'role': CustomUser.Role.MEMBER,
                'title': 'Principal Product Designer',
                'bio': 'Obsessed with fluid micro-interactions, dark glassmorphism, and accessible design systems.',
                'avatar_color': 'emerald',
                'is_staff': False,
                'is_superuser': False,
            }
        )
        elena_user.set_password('MemberPass123!')
        elena_user.role = CustomUser.Role.MEMBER
        elena_user.save()

        self.stdout.write(self.style.SUCCESS('[OK] Demo accounts verified (admin, sarah_manager, alex_dev, elena_designer)'))

        # 2. Projects
        p1, _ = Project.objects.get_or_create(
            slug='fintech-mobile-app',
            defaults={
                'name': 'Fintech Mobile Banking App 2.0',
                'description': 'End-to-end rewrite of the customer financial dashboard with real-time analytics and biometric multi-factor authentication.',
                'color': 'indigo',
                'status': Project.Status.ACTIVE,
                'created_by': manager_user,
            }
        )
        p1.members.set([admin_user, manager_user, alex_user, elena_user])

        p2, _ = Project.objects.get_or_create(
            slug='cloud-security-hardening',
            defaults={
                'name': 'Cloud Security & Zero-Trust Architecture',
                'description': 'Implementing zero-trust session management, OAuth 2.0 PKCE, rate-limiting, and end-to-end token auditing.',
                'color': 'cyan',
                'status': Project.Status.ACTIVE,
                'created_by': admin_user,
            }
        )
        p2.members.set([admin_user, manager_user, alex_user])

        p3, _ = Project.objects.get_or_create(
            slug='design-system-refresh',
            defaults={
                'name': 'Design System & Neo-Glass UI Tokens',
                'description': 'Unified component library with fluid dark mode, accessible contrast ratios, and responsive layout primitives.',
                'color': 'purple',
                'status': Project.Status.PLANNING,
                'created_by': manager_user,
            }
        )
        p3.members.set([manager_user, elena_user, alex_user])

        self.stdout.write(self.style.SUCCESS('[OK] Demo projects populated'))

        # 3. Tasks
        Task.objects.all().delete()  # Clean demo task reset

        tasks_data = [
            {
                'title': 'Implement Secure Password Reset with Token Verification',
                'description': 'Configure Django token generation with secure email dispatches, single-use token expiration, and CSRF protection.',
                'project': p2,
                'assigned_to': alex_user,
                'created_by': admin_user,
                'status': Task.Status.DONE,
                'priority': Task.Priority.URGENT,
                'due_date': today - timedelta(days=2),
            },
            {
                'title': 'Design Responsive Navigation & Modern Dark Theme System',
                'description': 'Build CSS custom property tokens for glassmorphic cards, glowing borders, and accessible typography with Google Fonts.',
                'project': p3,
                'assigned_to': elena_user,
                'created_by': manager_user,
                'status': Task.Status.DONE,
                'priority': Task.Priority.HIGH,
                'due_date': today - timedelta(days=1),
            },
            {
                'title': 'Develop Interactive Kanban Board & Status Pipeline',
                'description': 'Build smooth column layout for To Do, In Progress, In Review, and Done cards with 1-click status transitions.',
                'project': p1,
                'assigned_to': alex_user,
                'created_by': manager_user,
                'status': Task.Status.IN_PROGRESS,
                'priority': Task.Priority.HIGH,
                'due_date': today + timedelta(days=2),
            },
            {
                'title': 'Configure Role-Based Access Control (Admin vs Regular)',
                'description': 'Restrict administrative actions, user role elevations, and project deletions to verified administrators.',
                'project': p2,
                'assigned_to': admin_user,
                'created_by': admin_user,
                'status': Task.Status.IN_PROGRESS,
                'priority': Task.Priority.URGENT,
                'due_date': today + timedelta(days=3),
            },
            {
                'title': 'Audit Account Registration & Password Validation Rules',
                'description': 'Verify min-length 8 characters, numeric validator, and duplicate email prevention logic across all signups.',
                'project': p2,
                'assigned_to': alex_user,
                'created_by': manager_user,
                'status': Task.Status.IN_REVIEW,
                'priority': Task.Priority.MEDIUM,
                'due_date': today + timedelta(days=1),
            },
            {
                'title': 'Export Transaction History to PDF & CSV Format',
                'description': 'Allow users to filter date ranges and download cryptographically signed statement receipts.',
                'project': p1,
                'assigned_to': alex_user,
                'created_by': manager_user,
                'status': Task.Status.TODO,
                'priority': Task.Priority.MEDIUM,
                'due_date': today + timedelta(days=5),
            },
            {
                'title': 'Create Micro-Interaction Hover States for Task Cards',
                'description': 'Add subtle scale transitions, elevation shadows, and pill tag animations for enhanced feedback.',
                'project': p3,
                'assigned_to': elena_user,
                'created_by': elena_user,
                'status': Task.Status.TODO,
                'priority': Task.Priority.LOW,
                'due_date': today + timedelta(days=6),
            },
            {
                'title': 'Implement Automated Session Timeout for Inactive Users',
                'description': 'Clear session cookies after 15 minutes of inactivity if Remember Me was left unchecked.',
                'project': p2,
                'assigned_to': admin_user,
                'created_by': admin_user,
                'status': Task.Status.TODO,
                'priority': Task.Priority.HIGH,
                'due_date': today + timedelta(days=4),
            },
        ]

        created_tasks = []
        for tdata in tasks_data:
            t = Task.objects.create(**tdata)
            created_tasks.append(t)

        self.stdout.write(self.style.SUCCESS(f'[OK] Created {len(created_tasks)} sample tasks across projects'))

        # 4. Comments
        Comment.objects.create(
            task=created_tasks[0],
            author=admin_user,
            content="Tokens are confirmed working with Django's built-in token generators and secure single-use invalidation."
        )
        Comment.objects.create(
            task=created_tasks[0],
            author=alex_user,
            content="Local file-based email preview backend is hooked up so developers can click reset links right away!"
        )
        Comment.objects.create(
            task=created_tasks[2],
            author=elena_user,
            content="I uploaded the updated color tokens for the Kanban column headers. Contrast looks crisp in both themes."
        )

        # 5. Activity Logs
        ActivityLog.objects.all().delete()
        ActivityLog.objects.create(
            user=admin_user,
            action="Configured role-based access control and admin security hub",
            project=p2
        )
        ActivityLog.objects.create(
            user=alex_user,
            action="Completed 'Implement Secure Password Reset with Token Verification'",
            task=created_tasks[0],
            project=p2
        )
        ActivityLog.objects.create(
            user=manager_user,
            action="Created project 'Fintech Mobile Banking App 2.0'",
            project=p1
        )
        ActivityLog.objects.create(
            user=elena_user,
            action="Completed 'Design Responsive Navigation & Modern Dark Theme System'",
            task=created_tasks[1],
            project=p3
        )
        ActivityLog.objects.create(
            user=alex_user,
            action="Moved 'Develop Interactive Kanban Board & Status Pipeline' to In Progress",
            task=created_tasks[2],
            project=p1
        )

        self.stdout.write(self.style.SUCCESS('[OK] Sample comments and audit logs generated.'))
        self.stdout.write(self.style.SUCCESS('[DONE] TaskFlow database seeding complete!'))
