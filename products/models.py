from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils.text import slugify
from django.urls import reverse


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
        if not self.slug:
            # Générer un slug à partir du nom
            self.slug = slugify(self.name)
            
            # Vérifier l'unicité du slug
            i = 1
            original_slug = self.slug
            while Product.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{i}"
                i += 1
        
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


