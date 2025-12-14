from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    
    # URLs d'authentification
    path('compte/inscription/', views.RegisterView.as_view(), name='register'),
    path('compte/connexion/', auth_views.LoginView.as_view(template_name='core/registration/login.html'), name='login'),
    path('compte/deconnexion/', auth_views.LogoutView.as_view(next_page='core:home'), name='logout'),
    
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
    path('gestion/produits/ajouter/', views.ProductCreateView.as_view(), name='product_add'),
    path('gestion/produits/<int:pk>/modifier/', views.ProductUpdateView.as_view(), name='product_update'),
    path('gestion/produits/<int:pk>/supprimer/', views.ProductDeleteView.as_view(), name='product_delete'),
    
    # Gestion des utilisateurs
    path('gestion/utilisateurs/', views.UserListView.as_view(), name='user_list'),
    path('gestion/utilisateurs/ajouter/', views.UserCreateView.as_view(), name='user_add'),
    path('gestion/utilisateurs/<int:pk>/modifier/', views.UserUpdateView.as_view(), name='user_update'),
    path('gestion/utilisateurs/<int:pk>/supprimer/', views.UserDeleteView.as_view(), name='user_delete'),
]
