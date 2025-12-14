from django.urls import path
from . import views
from . import views_admin

app_name = 'orders'

urlpatterns = [
    # URLs publiques
    path('mes-commandes/', views.order_list, name='order_list'),
    path('commande/creer/', views.order_create, name='order_create'),
    path('facture/<int:order_id>/', views.order_invoice, name='invoice'),
    
    # URLs d'administration personnalisées
    path('admin/commandes/', views_admin.OrderListView.as_view(), name='admin_order_list'),
    path('admin/commandes/<int:pk>/', views_admin.OrderDetailView.as_view(), name='admin_order_detail'),
    path('admin/commandes/<int:pk>/modifier/', views_admin.OrderUpdateView.as_view(), name='admin_order_update'),
    path('admin/commandes/<int:pk>/payer/', views_admin.mark_as_paid, name='admin_mark_as_paid'),
]
