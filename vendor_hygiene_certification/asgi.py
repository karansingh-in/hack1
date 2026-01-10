import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vendor_hygiene_certification.settings')

application = get_asgi_application()
