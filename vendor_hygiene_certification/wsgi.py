import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vendor_hygiene_certification.settings')

application = get_wsgi_application()
