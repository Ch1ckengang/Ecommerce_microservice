import sys
import os
import django

# Setup Django
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frontend_service.settings')
django.setup()

from django.contrib.sessions.models import Session
from django.utils import timezone

# Get all active sessions
active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
print(f"Active sessions: {active_sessions.count()}")

for session in active_sessions:
    session_data = session.get_decoded()
    if 'user_id' in session_data:
        print(f"\nSession: {session.session_key[:10]}...")
        print(f"  User ID: {session_data.get('user_id')}")
        print(f"  Username: {session_data.get('username')}")
        print(f"  Has token: {'access_token' in session_data}")
        print(f"  Expires: {session.expire_date}")
