from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, ListView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils import timezone
from django.db.models import Sum, F, Value
from django.db.models.functions import Coalesce

from .models import Product, Stock, Category
from .forms import StockForm


class StockEntryCreateView(LoginRequiredMixin, CreateView):
    model = Stock
    form_class = StockForm
    template_name = 'products/stock_entry_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = get_object_or_404(Product, pk=self.kwargs['product_id'])
        return context
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['product'] = get_object_or_404(Product, pk=self.kwargs['product_id'])
        return kwargs
    
    def form_valid(self, form):
        product = get_object_or_404(Product, pk=self.kwargs['product_id'])
        stock_entry = form.save(commit=False)
        stock_entry.product = product
        
        # Déterminer si c'est un ajout ou un retrait
        operation_type = form.cleaned_data.get('operation_type', 'add')
        if operation_type == 'remove':
            stock_entry.quantity = -abs(stock_entry.quantity)
        
        stock_entry.save()
        
        # Mettre à jour la disponibilité du produit
        product.refresh_from_db()
        if product.current_stock <= 0 and product.available:
            product.available = False
            product.save()
        elif product.current_stock > 0 and not product.available:
            product.available = True
            product.save()
        
        messages.success(
            self.request,
            f"Stock mis à jour avec succès pour {product.name}. "
            f"Nouvelle quantité en stock : {product.current_stock}"
        )
        return redirect('products:stock_management')


class StockHistoryView(LoginRequiredMixin, ListView):
    model = Stock
    template_name = 'products/stock_history.html'
    context_object_name = 'stock_entries'
    paginate_by = 20
    
    def get_queryset(self):
        self.product = get_object_or_404(Product, pk=self.kwargs['product_id'])
        return Stock.objects.filter(product=self.product).order_by('-date_entree')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.product
        return context


class StockManagementView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'products/stock_management.html'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Récupérer tous les produits avec leur stock actuel
        products = Product.objects.annotate(
            current_stock=Coalesce(
                Sum('stock_entries__quantity'),
                Value(0)
            )
        ).order_by('name')
        
        # Filtrer par catégorie si spécifié
        category_id = self.request.GET.get('category')
        if category_id:
            products = products.filter(category_id=category_id)
        
        # Filtrer par disponibilité si spécifié
        available = self.request.GET.get('available')
        if available == 'in_stock':
            products = products.filter(stock_entries__quantity__gt=0).distinct()
        elif available == 'out_of_stock':
            products = products.filter(stock_entries__isnull=True) | products.filter(
                stock_entries__quantity__lte=0
            ).distinct()
        
        # Préparer les données pour le template
        products_with_stock = []
        for product in products:
            products_with_stock.append({
                'id': product.id,
                'name': product.name,
                'category': product.category,
                'current_stock': product.current_stock,
                'available': product.available,
                'price': product.price,
                'image': product.image,
            })
        
        context.update({
            'products': products_with_stock,
            'categories': Category.objects.all(),
            'selected_category': category_id if category_id else '',
            'selected_availability': available or ''
        })
        
        return context
