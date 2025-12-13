from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from products.models import Product, Category
from .forms import CategoryForm, ProductForm


def home(request):
    # Récupérer les produits en vedette (par exemple, les 8 premiers produits disponibles)
    featured_products = Product.objects.filter(available=True)[:8]
    # Récupérer toutes les catégories pour le menu
    categories = Category.objects.all()
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'core/home.html', context)


def product_list(request, category_slug=None):
    """Affiche la liste des produits, éventuellement filtrés par catégorie"""
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    context = {
        'category': category,
        'categories': categories,
        'products': products,
    }
    return render(request, 'core/product/list.html', context)


def product_detail(request, id, slug):
    """Affiche les détails d'un produit spécifique"""
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    context = {
        'product': product,
        'page_title': product.name,
    }
    return render(request, 'core/product/detail.html', context)


@login_required
def admin_dashboard(request):
    """Vue du tableau de bord administrateur"""
    # Vérifier que l'utilisateur est un administrateur
    if not request.user.is_staff and not request.user.is_superuser:
        return HttpResponseForbidden("Accès refusé")
    
    context = {
        'page_title': 'Tableau de bord administrateur',
        'product_count': Product.objects.count(),
        'order_count': 0,  # À remplacer par le modèle Order quand il sera créé
        'user_count': 0,    # À remplacer par le modèle User quand il sera créé
    }
    return render(request, 'core/admin/dashboard.html', context)


# Vues basées sur les classes pour la gestion des catégories
class CategoryListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Category
    template_name = 'core/admin/category_list.html'
    context_object_name = 'categories'
    paginate_by = 10
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class CategoryCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'core/admin/category_form.html'
    success_url = reverse_lazy('core:category_list')
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def form_valid(self, form):
        messages.success(self.request, 'La catégorie a été ajoutée avec succès.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Ajouter une catégorie'
        return context


class CategoryUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'core/admin/category_form.html'
    success_url = reverse_lazy('core:category_list')
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.object:
            kwargs['instance'] = self.object
            kwargs['initial'] = {'code': self.object.slug}
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, 'La catégorie a été mise à jour avec succès.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Modifier la catégorie: {self.object.name}'
        return context


class CategoryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Category
    template_name = 'core/admin/category_confirm_delete.html'
    success_url = reverse_lazy('core:category_list')
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'La catégorie a été supprimée avec succès.')
        return super().delete(request, *args, **kwargs)


# Vues pour la gestion des produits
class ProductListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Product
    template_name = 'core/admin/product_list.html'
    context_object_name = 'products'
    paginate_by = 10
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class ProductCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'core/admin/product_form.html'
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def form_valid(self, form):
        # Vérifier si un produit avec le même nom existe déjà dans la même catégorie
        name = form.cleaned_data.get('name')
        category = form.cleaned_data.get('category')
        if Product.objects.filter(name__iexact=name, category=category).exists():
            form.add_error('name', f'Un produit avec ce nom existe déjà dans la catégorie {category}.')
            return self.form_invalid(form)
            
        messages.success(self.request, 'Le produit a été ajouté avec succès.')
        return super().form_valid(form)
        
    def form_invalid(self, form):
        # Afficher les erreurs de formulaire dans les messages
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{form.fields[field].label}: {error}")
        return super().form_invalid(form)
    
    def get_success_url(self):
        # Rediriger vers la liste des produits dans l'administration
        return reverse_lazy('core:product_list_admin')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Ajouter un produit'
        return context


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'core/admin/product_form.html'
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def form_valid(self, form):
        # Vérifier si un autre produit avec le même nom existe déjà dans la même catégorie
        name = form.cleaned_data.get('name')
        category = form.cleaned_data.get('category')
        if Product.objects.filter(
            name__iexact=name, 
            category=category
        ).exclude(id=self.object.id).exists():
            form.add_error('name', f'Un autre produit avec ce nom existe déjà dans la catégorie {category}.')
            return self.form_invalid(form)
            
        messages.success(self.request, 'Le produit a été mis à jour avec succès.')
        return super().form_valid(form)
        
    def form_invalid(self, form):
        # Afficher les erreurs de formulaire dans les messages
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{form.fields[field].label}: {error}")
        return super().form_invalid(form)
    
    def get_success_url(self):
        # Rediriger vers la liste des produits dans l'administration
        return reverse_lazy('core:product_list_admin')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Modifier le produit: {self.object.name}'
        return context


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    template_name = 'core/admin/product_confirm_delete.html'
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def get_success_url(self):
        # Rediriger vers la liste des produits dans l'administration
        return reverse_lazy('core:product_list_admin')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Le produit a été supprimé avec succès.')
        return super().delete(request, *args, **kwargs)
