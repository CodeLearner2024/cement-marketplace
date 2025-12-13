import os
import django

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'store.settings')
django.setup()

from products.models import Product
from django.utils.text import slugify

def update_product_slugs():
    # Récupérer tous les produits sans slug
    products_without_slug = Product.objects.filter(slug='')
    
    # Mettre à jour les slugs manquants
    for product in products_without_slug:
        # Sauvegarder le produit pour déclencher la méthode save()
        product.save()
        print(f"Mis à jour le slug pour {product.name} : {product.slug}")
    
    print("Mise à jour des slugs terminée.")

if __name__ == "__main__":
    update_product_slugs()
