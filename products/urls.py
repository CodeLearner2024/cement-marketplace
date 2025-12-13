from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # URLs pour la gestion du stock
    path('stock/', views.StockManagementView.as_view(), name='stock_management'),
    path('stock/entry/<int:product_id>/', views.StockEntryCreateView.as_view(), name='stock_entry'),
    path('stock/history/', views.StockHistoryView.as_view(), name='stock_history_all'),
    path('stock/history/<int:product_id>/', views.StockHistoryView.as_view(), name='stock_history'),
    
    # URL pour afficher les détails d'un produit
    path('product/<int:pk>/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    
    # URL pour lister les produits
    path('', views.ProductListView.as_view(), name='product_list'),
]
