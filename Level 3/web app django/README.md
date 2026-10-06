# TaskFlow

TaskFlow is a Django web application for managing team projects and tasks. It helps teams create projects, assign and track tasks, set priorities and due dates, collaborate through comments, and review activity in one place.

## Features

- User registration, login, profiles, and password reset
- Role-based access for administrators, project managers, and team members
- Project and task management with status, priority, assignees, and due dates
- Task comments and an activity log for team collaboration
- Dashboard and admin interface

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in your browser. The project uses SQLite by default.
