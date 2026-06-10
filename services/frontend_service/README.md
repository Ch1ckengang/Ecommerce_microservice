# Frontend Service

Django-based frontend service for the e-commerce microservices system.

## Features

- Server-side rendered HTML templates
- Integration with backend microservices
- Session-based authentication
- Responsive design with Tailwind CSS
- Static file serving

## Structure

```
frontend_service/
├── frontend_service/     # Django project settings
├── pages/               # Main app for views and templates
│   ├── templates/       # HTML templates
│   ├── static/          # CSS, JS, images
│   ├── views.py         # View controllers
│   └── urls.py          # URL routing
├── manage.py
├── requirements.txt
├── Dockerfile
└── entrypoint.sh
```

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Run development server
python manage.py runserver 0.0.0.0:8000
```

## Docker

```bash
# Build image
docker build -t frontend-service .

# Run container
docker run -p 8000:8000 frontend-service
```

## Environment Variables

See `.env.example` for required environment variables.
