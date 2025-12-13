from django.contrib import admin
from .models import Conversation


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """Configuration de l'administration pour le modèle Conversation"""
    list_display = ('id', 'user', 'get_intent_display', 'created_at', 'is_resolved', 'requires_followup')
    list_filter = ('intent', 'is_resolved', 'requires_followup', 'created_at')
    search_fields = ('user_message', 'bot_response', 'user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    list_select_related = ('user',)
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('user', 'session_key', 'intent')
        }),
        ('Messages', {
            'fields': ('user_message', 'bot_response')
        }),
        ('Métadonnées', {
            'fields': ('is_resolved', 'requires_followup', 'metadata'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Rend certains champs en lecture seule lors de l'édition"""
        if obj:  # Si on modifie un objet existant
            return self.readonly_fields + ('user', 'session_key', 'intent', 'user_message')
        return self.readonly_fields
