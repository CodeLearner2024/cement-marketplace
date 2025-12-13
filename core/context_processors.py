from products.models import Category
from cart.cart import Cart

def ecommerce_processor(request):
    """Ajoute des variables communes au contexte de toutes les vues."""
    context = {
        'categories': Category.objects.all()
    }
    
    # Ajouter le panier si l'utilisateur est authentifié
    if hasattr(request, 'user') and request.user.is_authenticated:
        context['cart'] = Cart(request)
    
    return context
