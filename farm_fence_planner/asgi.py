import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_fence_planner.settings')
application = get_asgi_application()
