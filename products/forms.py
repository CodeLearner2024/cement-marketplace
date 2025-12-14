from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import StockMovement, Product, StockMovementType


class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ['product', 'movement_type', 'quantity', 'reference', 'movement_date', 'notes']
        widgets = {
            'movement_date': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control',
                    'max': timezone.now().strftime('%Y-%m-%dT%H:%M')
                },
                format='%Y-%m-%dT%H:%M'
            ),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Notes supplémentaires...'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'step': 1
            }),
            'reference': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Référence (facultatif)'
            }),
        }
        labels = {
            'product': 'Produit',
            'movement_type': 'Type de mouvement',
            'quantity': 'Quantité',
            'reference': 'Référence',
            'movement_date': 'Date et heure',
            'notes': 'Notes'
        }

    def __init__(self, *args, **kwargs):
        product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)
        
        if product:
            self.fields['product'].initial = product
            self.fields['product'].widget = forms.HiddenInput()
        
        # Définir la date et l'heure par défaut
        self.fields['movement_date'].initial = timezone.now()
        
        # Personnaliser le champ de type de mouvement
        self.fields['movement_type'].choices = StockMovementType.choices
        self.fields['movement_type'].widget.attrs.update({
            'class': 'form-select'
        })
    
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity <= 0:
            raise ValidationError("La quantité doit être supérieure à zéro")
        return quantity
    
    def clean(self):
        cleaned_data = super().clean()
        movement_type = cleaned_data.get('movement_type')
        quantity = cleaned_data.get('quantity')
        product = cleaned_data.get('product')
        
        if movement_type and quantity and product:
            # Pour les sorties, vérifier qu'il y a assez de stock
            if movement_type in [StockMovementType.OUT, StockMovementType.LOSS]:
                if quantity > product.stock_quantity:
                    raise ValidationError({
                        'quantity': f"Stock insuffisant. Stock actuel: {product.stock_quantity}"
                    })
        
        return cleaned_data


class ProductStockForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['stock_quantity']
        labels = {
            'stock_quantity': 'Nouvelle quantité en stock'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['stock_quantity'].widget.attrs.update({
            'class': 'form-control',
            'min': 0,
            'step': 1
        })
    
    def save(self, commit=True):
        # La logique de sauvegarde est gérée dans la vue
        return super().save(commit=commit)
