from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from products.models import Product


class Order(models.Model):
    """Modèle pour les commandes passées par les clients"""
    STATUS_CHOICES = [
        ('en_attente', 'En attente de paiement'),
        ('payee', 'Payée'),
        ('en_preparation', 'En préparation'),
        ('expediee', 'Expédiée'),
        ('livree', 'Livrée'),
        ('annulee', 'Annulée'),
        ('remboursee', 'Remboursée'),
    ]

    DELIVERY_CHOICES = [
        ('retrait', 'Retrait en magasin'),
        ('livraison', 'Livraison à domicile'),
    ]

    PAYMENT_METHODS = [
        ('lumicash', 'Lumicash'),
        ('ecocash', 'EcoCash'),
        ('ihela', 'Ihela'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name="Client"
    )
    first_name = models.CharField(max_length=50, verbose_name="Prénom")
    last_name = models.CharField(max_length=50, verbose_name="Nom")
    email = models.EmailField(verbose_name="Email")
    delivery_type = models.CharField(
        max_length=20,
        choices=DELIVERY_CHOICES,
        default='retrait',
        verbose_name="Type de livraison"
    )
    address = models.CharField(
        max_length=250, 
        verbose_name="Adresse complète",
        blank=True,
        null=True,
        help_text="Remplir uniquement pour une livraison à domicile"
    )
    postal_code = models.CharField(
        max_length=20, 
        verbose_name="Code postal",
        blank=True,
        null=True
    )
    city = models.CharField(
        max_length=100, 
        verbose_name="Ville",
        blank=True,
        null=True
    )
    phone = models.CharField(max_length=20, verbose_name="Téléphone")
    notes = models.TextField(blank=True, verbose_name="Notes")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='en_attente',
        verbose_name="Statut"
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        verbose_name="Méthode de paiement"
    )
    paid = models.BooleanField(default=False, verbose_name="Payé")
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Montant total"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f'Commande {self.id}'
        
    def get_total_cost(self):
        """Calcule le coût total de la commande"""
        return sum(item.get_cost() for item in self.items.all())
        
    def get_status_color(self):
        """Retourne la classe CSS correspondant au statut de la commande"""
        status_colors = {
            'en_attente': 'warning',
            'payee': 'info',
            'en_preparation': 'primary',
            'expediee': 'info',
            'livree': 'success',
            'annulee': 'danger',
            'remboursee': 'secondary',
        }
        return status_colors.get(self.status, 'secondary')


class OrderItem(models.Model):
    """Article individuel dans une commande"""
    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE,
        verbose_name="Commande"
    )
    product = models.ForeignKey(
        Product,
        related_name='order_items',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Produit"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Prix unitaire"
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Quantité"
    )

    class Meta:
        verbose_name = "Article de commande"
        verbose_name_plural = "Articles de commande"

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    def get_cost(self):
        """Calcule le coût total pour cet article"""
        return self.price * self.quantity
