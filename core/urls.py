from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from . import views

# Import des vues de l'application products
from products.views import (
    StockManagementView, 
    StockEntryCreateView, 
    StockHistoryView
)

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    
    # URLs d'authentification
    path('accounts/login/', auth_views.LoginView.as_view(template_name='core/registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='core:home'), name='logout'),
    
    # Tableau de bord administrateur
    path('gestion/dashboard/', login_required(views.admin_dashboard), name='admin_dashboard'),
    
    # Gestion des catégories
    path('gestion/categories/', views.CategoryListView.as_view(), name='category_list'),
    path('gestion/categories/ajouter/', views.CategoryCreateView.as_view(), name='category_create'),
    path('gestion/categories/<int:pk>/modifier/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('gestion/categories/<int:pk>/supprimer/', views.CategoryDeleteView.as_view(), name='category_delete'),
    
    # Détail d'un produit
    path('produit/<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    
    # Liste des produits par catégorie
    path('categorie/<slug:category_slug>/', views.product_list, name='product_list'),
    
    # Gestion des produits
    path('gestion/produits/', views.ProductListView.as_view(), name='product_list_admin'),
    path('gestion/produits/ajouter/', views.ProductCreateView.as_view(), name='product_create'),
    path('gestion/produits/<int:pk>/modifier/', views.ProductUpdateView.as_view(), name='product_update'),
    path('gestion/produits/<int:pk>/supprimer/', views.ProductDeleteView.as_view(), name='product_delete'),
    
    # Gestion du stock
    path('gestion/stock/', StockManagementView.as_view(), name='stock_management'),
    path('gestion/stock/entree/<int:product_id>/', StockEntryCreateView.as_view(), name='stock_entry'),
    path('gestion/stock/historique/', StockHistoryView.as_view(), name='stock_history_all'),
    path('gestion/stock/historique/<int:product_id>/', StockHistoryView.as_view(), name='stock_history'),
]
