from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone
from django.db.models import Sum, F
from django.db.models.functions import Coalesce


class Category(models.Model):
    """Catégorie de produits (Ciment, Sable, etc.)"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom")
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    """Modèle pour les produits de ciment"""
    CEMENT_TYPES = [
        ('CPJ45', 'Ciment Portland 45'),
        ('CPJ35', 'Ciment Portland 35'),
        ('CPJ32.5', 'Ciment Portland 32.5'),
        ('CPJ42.5', 'Ciment Portland 42.5'),
        ('CPJ52.5', 'Ciment Portland 52.5'),
        ('CPA', 'Ciment Portland Artificiel'),
        ('HTS', 'Haut Fourneau'),
        ('LHP', 'Laitier Haut Fourneau Moulu'),
    ]
    
    class Meta:
        unique_together = ('name', 'category')
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['name']
        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['name']),
            models.Index(fields=['-created_at']),
        ]

    name = models.CharField(max_length=200, verbose_name="Nom du produit")
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True, verbose_name="Description")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    cement_type = models.CharField(
        max_length=10, 
        choices=CEMENT_TYPES,
        verbose_name="Type de ciment"
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Prix unitaire (BIF)"
    )
    weight = models.DecimalField(
        max_digits=6, 
        decimal_places=2,
        verbose_name="Poids (kg)",
        help_text="Poids d'un sac en kilogrammes"
    )
    image = models.ImageField(
        upload_to='products/%Y/%m/%d', 
        blank=True,
        verbose_name="Image du produit"
    )
    available = models.BooleanField(
        default=True,
        verbose_name="Disponible",
        help_text="Le produit est-il disponible à la vente ?"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def stock_quantity(self):
        """Retourne la quantité totale en stock pour ce produit"""
        total = self.stock_entries.aggregate(
            total=Sum('quantity')
        )['total']
        return total if total is not None else 0

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['name']
        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['name']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_cement_type_display()})"
        
    def save(self, *args, **kwargs):
        from django.utils.text import slugify
        from django.db import transaction
        
        if not self.slug:
            # Générer un slug à partir du nom
            self.slug = slugify(self.name)
            
            # Vérifier l'unicité du slug
            with transaction.atomic():
                slugs = set(
                    Product.objects
                    .filter(slug__startswith=self.slug)
                    .values_list('slug', flat=True)
                )
                
                # Si le slug existe déjà, ajouter un numéro incrémentiel
                if self.slug in slugs:
                    i = 1
                    while f"{self.slug}-{i}" in slugs:
                        i += 1
                    self.slug = f"{self.slug}-{i}"
        
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('core:product_detail', args=[self.id, self.slug])

    @property
    def stock_quantity(self):
        """Retourne la quantité totale en stock pour ce produit"""
        total = self.stock_entries.aggregate(
            total=Coalesce(Sum('quantity'), 0)
        )['total']
        return total if total > 0 else 0


class Stock(models.Model):
    """Modèle pour gérer les entrées en stock des produits"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='stock_entries',
        verbose_name="Produit"
    )
    quantity = models.IntegerField(
        verbose_name="Quantité",
        help_text="Quantité à ajouter au stock (positive pour ajouter, négative pour retirer)",
        default=0
    )
    date_entree = models.DateTimeField(
        default=timezone.now,
        verbose_name="Date d'entrée"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notes"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mouvement de stock"
        verbose_name_plural = "Mouvements de stock"
        ordering = ['-date_entree']

    def __str__(self):
        action = "Ajout" if self.quantity >= 0 else "Retrait"
        return f"{action} de {abs(self.quantity)} {self.product.name} le {self.date_entree.strftime('%d/%m/%Y')}"

    def save(self, *args, **kwargs):
        # S'assurer que la date d'entrée est définie
        if not self.date_entree:
            self.date_entree = timezone.now()
            
        # Vérifier si une entrée similaire existe déjà
        if self.pk is None:  # Nouvelle entrée
            existing_entry = Stock.objects.filter(
                product=self.product,
                date_entree__date=self.date_entree.date(),
                notes=self.notes
            ).first()
            
            if existing_entry:
                # Mettre à jour la quantité existante au lieu de créer une nouvelle entrée
                existing_entry.quantity += self.quantity
                existing_entry.save()
                self.product.save()  # Mettre à jour le produit après la mise à jour du stock
                return existing_entry
                
        # Sauvegarder l'entrée de stock
        result = super().save(*args, **kwargs)
        # Mettre à jour le stock du produit
        self.product.save()
        return result
