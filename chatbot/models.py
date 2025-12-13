from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Conversation(models.Model):
    """Modèle pour stocker les conversations avec le chatbot"""
    class IntentType(models.TextChoices):
        GREETING = 'greeting', _('Salutation')
        PRODUCT_INFO = 'product_info', _('Information sur le produit')
        ORDER_STATUS = 'order_status', _('Statut de commande')
        DELIVERY_INFO = 'delivery_info', _('Information de livraison')
        PAYMENT_INFO = 'payment_info', _('Information de paiement')
        COMPLAINT = 'complaint', _('Réclamation')
        THANKS = 'thanks', _('Remerciement')
        GOODBYE = 'goodbye', _('Au revoir')
        OTHER = 'other', _('Autre')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conversations',
        verbose_name=_("Utilisateur")
    )
    session_key = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Clé de session")
    )
    intent = models.CharField(
        max_length=20,
        choices=IntentType.choices,
        default=IntentType.OTHER,
        verbose_name=_("Intention")
    )
    user_message = models.TextField(verbose_name=_("Message de l'utilisateur"))
    bot_response = models.TextField(verbose_name=_("Réponse du bot"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Date de création"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Dernière mise à jour"))
    is_resolved = models.BooleanField(default=False, verbose_name=_("Résolu"))
    requires_followup = models.BooleanField(default=False, verbose_name=_("Suivi requis"))
    metadata = models.JSONField(default=dict, blank=True, verbose_name=_("Métadonnées"))

    class Meta:
        verbose_name = _("Conversation")
        verbose_name_plural = _("Conversations")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['session_key']),
            models.Index(fields=['intent']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Conversation {self.id} - {self.get_intent_display()} - {self.created_at}"

    @property
    def is_anonymous(self):
        """Vérifie si la conversation est anonyme (sans utilisateur connecté)"""
        return self.user is None

    def mark_as_resolved(self):
        """Marque la conversation comme résolue"""
        self.is_resolved = True
        self.save(update_fields=['is_resolved', 'updated_at'])
