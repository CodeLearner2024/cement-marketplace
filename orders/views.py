from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.http import HttpResponseForbidden, HttpResponse
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
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
            try:
                # Créer la commande sans la sauvegarder
                order = form.save(commit=False)
                order.user = request.user
                order.total_amount = cart.get_total_price()
                
                # Si c'est un retrait en magasin, on efface les champs d'adresse
                if order.delivery_type == 'retrait':
                    order.address = None
                    order.postal_code = None
                    order.city = None
                
                # Sauvegarder la commande
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
                        fail_silently=True
                    )
                except Exception as e:
                    # En cas d'erreur d'envoi d'email, on continue quand même
                    print(f"Erreur d'envoi d'email: {e}")
                
                # Vider le panier
                cart.clear()
                
                # Ajouter un message de succès
                messages.success(request, 'Votre commande a été passée avec succès !')
                
                # Rediriger vers la page de facture
                return redirect('orders:invoice', order_id=order.id)
                
            except Exception as e:
                # En cas d'erreur, on affiche un message d'erreur
                messages.error(request, f"Une erreur est survenue lors de la création de votre commande: {str(e)}")
                # On ne vide pas le panier en cas d'erreur
        else:
            # Afficher les erreurs de formulaire
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{form.fields[field].label}: {error}")
    else:
        # Pré-remplir le formulaire avec les informations de l'utilisateur
        initial_data = {
            'first_name': request.user.first_name or '',
            'last_name': request.user.last_name or '',
            'email': request.user.email or '',
            'phone': request.user.phone if hasattr(request.user, 'phone') and request.user.phone else '',
        }
        form = OrderCreateForm(initial=initial_data)
    
    return render(request, 'orders/order/create.html', {
        'cart': cart,
        'form': form,
        'title': 'Passer la commande'
    })

@login_required
@login_required
def order_list(request):
    """Affiche la liste des commandes de l'utilisateur avec tri par date"""
    # Récupérer le paramètre de tri
    sort_by = request.GET.get('sort', '-created_at')
    
    # Valider le paramètre de tri pour éviter les injections
    if sort_by not in ['created_at', '-created_at', 'updated_at', '-updated_at']:
        sort_by = '-created_at'
    
    # Récupérer les commandes de l'utilisateur connecté
    orders = Order.objects.filter(user=request.user).order_by(sort_by)
    
    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(orders, 10)  # 10 commandes par page
    
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)
    
    context = {
        'orders': orders,
        'sort_by': sort_by,
    }
    
    return render(request, 'orders/order/list.html', context)

def order_invoice(request, order_id):
    """Vue pour afficher la facture d'une commande"""
    order = get_object_or_404(Order, id=order_id)
    
    # Vérifier que l'utilisateur est bien le propriétaire de la commande
    if order.user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("Vous n'êtes pas autorisé à voir cette facture.")
    
    from decimal import Decimal
    
    # Calculer le total TTC
    total_ttc = order.total_amount
    
    # Calculer la TVA (20% par défaut)
    tva_rate = Decimal('0.20')
    total_ht = total_ttc / (Decimal('1') + tva_rate)
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
