# KanMind Backend

Backend for the KanMind Kanban board frontend, built with Django and Django REST Framework.

## Setup

1. Create and activate a virtual environment:

```
python -m venv venv
source venv/Scripts/activate
```

2. Install dependencies:

```
pip install -r requirements.txt
```

3. Apply migrations:

```
python manage.py migrate
```

4. Create a superuser (optional, for /admin/):

```
python manage.py createsuperuser
```

5. Start the server:

```
python manage.py runserver
```

The API is available under http://127.0.0.1:8000/api/

## Notes

- Login uses a custom User model with email instead of username.
- Auth works with tokens. Get a token from POST /api/login/ or POST /api/registration/, then send it with every request as header: Authorization: Token <token>
- PATCH /api/boards/{id}/ returns a different response shape than GET /api/boards/{id}/ (owner_data/members_data instead of owner_id/members). This is intentional, matches the API spec.
- Built and tested with Python 3.14.

## Requirements

See requirements.txt.
