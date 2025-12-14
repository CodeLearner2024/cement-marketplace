from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone
from .models import Order, OrderItem

class OrderListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Order
    template_name = 'orders/admin/order_list.html'
    context_object_name = 'orders'
    paginate_by = 20

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        return Order.objects.select_related('user').order_by('-created_at')

class OrderDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Order
    template_name = 'orders/admin/order_detail.html'
    context_object_name = 'order'

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        return Order.objects.select_related('user').prefetch_related('items__product')

class OrderUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Order
    fields = ['status', 'delivery_type', 'payment_method', 'paid']
    template_name = 'orders/admin/order_form.html'
    success_url = reverse_lazy('orders:admin_order_list')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        # Si le paiement est marqué comme effectué, mettre à jour le statut
        if form.cleaned_data.get('paid') and form.cleaned_data.get('status') == 'en_attente':
            form.instance.status = 'payee'
        # Si le paiement n'est pas effectué, s'assurer que le statut n'est pas 'payee'
        elif not form.cleaned_data.get('paid') and form.cleaned_data.get('status') == 'payee':
            form.instance.status = 'en_attente'
            
        response = super().form_valid(form)
        messages.success(self.request, 'La commande a été mise à jour avec succès.')
        return response

def mark_as_paid(request, pk):
    if not request.user.is_staff:
        return redirect('home')
    
    order = Order.objects.get(pk=pk)
    order.paid = True
    order.status = 'payee'  # Mettre à jour le statut sur 'payee' (payée)
    order.updated_at = timezone.now()
    order.save()
    messages.success(request, f'La commande #{order.id} a été marquée comme payée.')
    return redirect('orders:admin_order_list')
