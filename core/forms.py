from django import forms
from django.core.exceptions import ValidationError
from products.models import Category, Product

class CategoryForm(forms.ModelForm):
    code = forms.SlugField(
        max_length=50,
        help_text="Code court et unique pour la catégorie (utilisé dans les URLs)"
    )
    
    class Meta:
        model = Category
        fields = ['name', 'code', 'description']
        labels = {
            'name': 'Libellé',
            'description': 'Description (optionnelle)'
        }
        help_texts = {
            'name': 'Nom complet de la catégorie',
        }
    
    def clean_code(self):
        code = self.cleaned_data.get('code')
        if not code:
            raise ValidationError("Le code est obligatoire")
        return code.lower()
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.slug = self.cleaned_data['code']
        if commit:
            instance.save()
        return instance


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'weight', 'price', 'image', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'price': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'weight': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'})
        }
        labels = {
            'name': 'Nom du produit',
            'category': 'Catégorie',
            'weight': 'Poids (kg)',
            'price': 'Prix unitaire (BIF)',
            'stock': 'Quantité en stock',
            'image': 'Image du produit',
            'description': 'Description (optionnelle)'
        }
        help_texts = {
            'price': 'Prix en francs burundais (BIF)',
            'weight': 'Poids d\'un sac en kilogrammes',
            'stock': 'Quantité disponible en stock',
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise ValidationError("Le prix ne peut pas être négatif")
        return price
        
    def clean_weight(self):
        weight = self.cleaned_data.get('weight')
        if weight is not None and weight <= 0:
            raise ValidationError("Le poids doit être supérieur à zéro")
        return weight
        
    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock is not None and stock < 0:
            raise ValidationError("La quantité en stock ne peut pas être négative")
        return stock
