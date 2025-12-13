from django.urls import re_path
from . import consumers

# Définit les modèles de routage WebSocket
websocket_urlpatterns = [
    re_path(r'ws/chatbot/$', consumers.ChatConsumer.as_asgi()),
]
