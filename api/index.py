import os
import sys

# Add the backend directory to Python path so Django can find all apps
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AdvIT.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
app = application
