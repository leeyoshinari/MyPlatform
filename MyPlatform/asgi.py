"""
ASGI config for MyPlatform project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MyPlatform.settings')
django.setup()


from django.core.asgi import get_asgi_application
from shell.channel import routing
from channels.routing import ProtocolTypeRouter, URLRouter
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    'websocket': URLRouter(routing.websocket_urlpatterns)
})
