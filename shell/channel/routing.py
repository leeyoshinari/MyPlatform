# from django.conf.urls import url
from django.urls import path, re_path
from . import websocket

websocket_urlpatterns = {
    re_path(r'openssh/host=$', websocket.WebSSH.as_asgi()),
    re_path(r'open/', websocket.WebSSH.as_asgi()),
}

