from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.conf import settings
from products.models import Product


class Cart(models.Model):
    """Modèle pour le panier d'achat"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name="Utilisateur"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Panier"
        verbose_name_plural = "Paniers"
        ordering = ['-created_at']

    def __str__(self):
        return f"Panier de {self.user.username}"

    @property
    def total_price(self):
        """Calcule le prix total du panier"""
        return sum(item.total_price for item in self.items.all())

    @property
    def total_quantity(self):
        """Calcule la quantité totale d'articles dans le panier"""
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    """Article individuel dans le panier"""
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Panier"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_items',
        verbose_name="Produit"
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name="Quantité"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Prix unitaire"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Article du panier"
        verbose_name_plural = "Articles du panier"
        unique_together = ['cart', 'product']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    @property
    def total_price(self):
        """Calcule le prix total pour cet article (prix unitaire * quantité)"""
        return self.price * self.quantity

    def save(self, *args, **kwargs):
        """Sauvegarde le prix actuel du produit lors de l'ajout au panier"""
        if not self.pk:  # Nouvel article
            self.price = self.product.price
        super().save(*args, **kwargs)
