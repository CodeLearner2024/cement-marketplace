from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('commande/creer/', views.order_create, name='order_create'),
    path('facture/<int:order_id>/', views.order_invoice, name='invoice'),
]
