from django.db import migrations
from django.utils.text import slugify

def update_slugs(apps, schema_editor):
    Product = apps.get_model('products', 'Product')
    for product in Product.objects.all():
        if not product.slug:
            product.slug = slugify(product.name)
            # Sauvegarder le produit pour générer un slug unique si nécessaire
            product.save(update_fields=['slug'])

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(update_slugs, reverse_code=migrations.RunPython.noop),
    ]
