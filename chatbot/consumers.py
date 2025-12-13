import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Conversation

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    """Consommateur WebSocket pour le chat en temps réel"""
    
    async def connect(self):
        """Établit la connexion WebSocket"""
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Rejoindre le groupe de chat
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        """Gère la déconnexion du WebSocket"""
        # Quitter le groupe de chat
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """Reçoit un message du WebSocket"""
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user = self.scope['user']
        
        # Enregistrer le message de l'utilisateur
        conversation = await self.save_conversation(
            user=user if user.is_authenticated else None,
            session_key=self.scope['session'].session_key,
            user_message=message,
            bot_response=""  # La réponse sera mise à jour par le traitement du chatbot
        )
        
        # Traiter le message avec le chatbot (à implémenter)
        bot_response = await self.process_message(message, conversation.id)
        
        # Mettre à jour la conversation avec la réponse du bot
        await self.update_conversation(conversation.id, bot_response)

        # Envoyer le message au groupe
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'bot_response': bot_response,
                'user': user.username if user.is_authenticated else 'Anonyme',
            }
        )

    async def chat_message(self, event):
        """Reçoit un message du groupe"""
        message = event['message']
        bot_response = event['bot_response']
        user = event['user']

        # Envoyer le message au WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'bot_response': bot_response,
            'user': user,
        }))

    @database_sync_to_async
    def save_conversation(self, user, session_key, user_message, bot_response):
        """Enregistre une conversation dans la base de données"""
        return Conversation.objects.create(
            user=user,
            session_key=session_key,
            user_message=user_message,
            bot_response=bot_response
        )
    
    @database_sync_to_async
    def update_conversation(self, conversation_id, bot_response):
        """Met à jour une conversation avec la réponse du bot"""
        Conversation.objects.filter(id=conversation_id).update(bot_response=bot_response)
    
    async def process_message(self, message, conversation_id):
        """Traite le message avec le chatbot et retourne une réponse"""
        # TODO: Implémenter la logique de traitement du message avec l'IA
        # Pour l'instant, on retourne une réponse simple
        return f"Je suis un chatbot IA. Vous avez dit : {message}"
