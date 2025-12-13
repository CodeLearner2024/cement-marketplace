from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from products.models import Product
from .cart import Cart

@require_POST
def cart_add(request, product_id):
    """Ajoute un produit au panier ou met à jour sa quantité."""
    if not request.user.is_authenticated:
        return JsonResponse(
            {'error': 'Authentication required'}, 
            status=403
        )
    
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    # Récupérer la quantité depuis les données POST
    quantity = int(request.POST.get('quantity', 1))
    
    # Ajouter ou mettre à jour le produit dans le panier
    cart.add(
        product=product,
        quantity=quantity,
        update_quantity=False
    )
    
    return JsonResponse({
        'success': True,
        'cart_item_count': cart.__len__()
    })

@require_POST
def cart_remove(request, product_id):
    """Supprime un produit du panier."""
    if not request.user.is_authenticated:
        return JsonResponse(
            {'error': 'Authentication required'}, 
            status=403
        )
    
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_item_count': cart.__len__(),
            'cart_total': str(cart.get_total_price())
        })
    return redirect('cart:cart_detail')

def cart_detail(request):
    """Affiche le panier avec tous les produits ajoutés."""
    cart = Cart(request)
    return render(request, 'cart/detail.html', {'cart': cart})
