"""
Common settings snippet to be added to all services
"""

CORS_SETTINGS = """
# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8080").split(",")
    if origin.strip()
]
CORS_ALLOW_CREDENTIALS = True
"""

SPECTACULAR_SETTINGS_TEMPLATE = """
# Swagger/OpenAPI Configuration
SPECTACULAR_SETTINGS = {
    "TITLE": "{service_name} API",
    "DESCRIPTION": "E-commerce {service_name} API Documentation",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}
"""
