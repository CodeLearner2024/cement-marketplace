from decimal import Decimal
from django.conf import settings

class Cart:
    def __init__(self, request):
        """Initialise le panier."""
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # Sauvegarder un panier vide dans la session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
        """Ajoute un produit au panier ou met à jour sa quantité."""
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price)
            }
        
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        
        self.save()

    def save(self):
        """Marque la session comme modifiée pour s'assurer qu'elle est sauvegardée."""
        self.session.modified = True

    def remove(self, product):
        """Supprime un produit du panier."""
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """Parcourt les articles du panier et récupère les produits depuis la base de données."""
        product_ids = self.cart.keys()
        # Récupérer les objets produit et les ajouter au panier
        from products.models import Product
        products = Product.objects.filter(id__in=product_ids)
        
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product
        
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """Compte tous les articles dans le panier."""
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """Calcule le coût total des articles dans le panier."""
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        )

    def clear(self):
        """Vide le panier."""
        del self.session[settings.CART_SESSION_ID]
        self.save()
