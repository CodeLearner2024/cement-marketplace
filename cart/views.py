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
            'cart_total': str(cart.get_total_price())  # Convert Decimal to string
        })
    return redirect('cart:cart_detail')

def cart_detail(request):
    """Affiche le panier avec tous les produits ajoutés."""
    cart = Cart(request)
    
    # Handle AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            # Create a serializable cart data structure
            cart_data = {
                'items': [],
                'total_price': str(cart.get_total_price()),
                'item_count': len(cart)
            }
            
            # Convert cart items to a serializable format
            for item in cart:
                item_data = {
                    'quantity': item.get('quantity', 0),
                    'price': str(item.get('price', 0)),
                    'total_price': str(item.get('total_price', 0)),
                }
                
                # Add product data if available
                if 'product' in item and hasattr(item['product'], 'id'):
                    item_data.update({
                        'product_id': item['product'].id,
                        'product_name': str(item['product'].name),
                        'image_url': str(item['product'].image.url) if hasattr(item['product'].image, 'url') else None,
                        'category_name': str(item['product'].category.name) if hasattr(item['product'], 'category') and item['product'].category else None
                    })
                
                cart_data['items'].append(item_data)
                    
            return JsonResponse(cart_data, safe=False)
            
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'items': [],
                'total_price': '0.00',
                'item_count': 0
            }, status=500)
    
    # For regular requests, pass the cart object directly to the template
    # The template will handle the rendering
    return render(request, 'cart/detail.html', {'cart': cart})
