from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.http import HttpResponseForbidden
from django.utils import timezone
from cart.cart import Cart
from .models import Order, OrderItem
from .forms import OrderCreateForm

@login_required
@require_http_methods(["GET", "POST"])
def order_create(request):
    cart = Cart(request)
    
    # Vérifier si le panier est vide
    if not cart:
        messages.error(request, "Votre panier est vide.")
        return redirect('cart:cart_detail')
    
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            # Créer la commande sans la sauvegarder
            order = form.save(commit=False)
            order.user = request.user
            order.total_amount = cart.get_total_price()
            
            # Si c'est un retrait en magasin, on efface les champs d'adresse
            if order.delivery_type == 'retrait':
                order.address = None
                order.postal_code = None
                order.city = None
            
            order.save()
            
            # Ajouter les articles de la commande
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )
            
            # Envoyer un email de confirmation
            try:
                subject = f'Confirmation de votre commande N°{order.id}'
                message = render_to_string('orders/order/email/order_created.html', {
                    'order': order,
                    'items': order.items.all(),
                    'total': order.total_amount
                })
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [order.email],
                    html_message=message,
                    fail_silently=False
                )
            except Exception as e:
                # En cas d'erreur d'envoi d'email, on continue quand même
                print(f"Erreur d'envoi d'email: {e}")
            
            # Vider le panier
            cart.clear()
            
            # Rediriger vers la page de facture
            return redirect('orders:invoice', order_id=order.id)
    else:
        # Pré-remplir le formulaire avec les informations de l'utilisateur
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'phone': request.user.phone if hasattr(request.user, 'phone') else '',
        }
        form = OrderCreateForm(initial=initial_data)
    
    return render(request, 'orders/order/create.html', {
        'cart': cart,
        'form': form,
    })

@login_required
def order_invoice(request, order_id):
    """Vue pour afficher la facture d'une commande"""
    order = get_object_or_404(Order, id=order_id)
    
    # Vérifier que l'utilisateur est bien le propriétaire de la commande
    if order.user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("Vous n'êtes pas autorisé à voir cette facture.")
    
    # Calculer le total TTC
    total_ttc = order.total_amount
    
    # Calculer la TVA (20% par défaut)
    tva_rate = 0.20
    total_ht = total_ttc / (1 + tva_rate)
    montant_tva = total_ttc - total_ht
    
    context = {
        'order': order,
        'items': order.items.all(),
        'total_ht': total_ht,
        'tva_rate': tva_rate * 100,  # Pourcentage
        'montant_tva': montant_tva,
        'total_ttc': total_ttc,
        'today': timezone.now().date(),
    }
    
    return render(request, 'orders/order/invoice.html', context)
