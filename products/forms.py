from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Stock, Product

class StockForm(forms.ModelForm):
    operation_type = forms.ChoiceField(
        choices=[
            ('add', 'Ajouter au stock'),
            ('remove', 'Retirer du stock')
        ],
        initial='add',
        widget=forms.RadioSelect,
        label='Type d\'opération'
    )
    
    class Meta:
        model = Stock
        fields = ['quantity', 'date_entree', 'notes']
        widgets = {
            'date_entree': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'max': timezone.now().strftime('%Y-%m-%d')
                }
            ),
            'notes': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Motif de l\'ajout/retrait...'
            }),
        }
        labels = {
            'quantity': 'Quantité',
            'date_entree': 'Date de l\'opération',
            'notes': 'Commentaire (optionnel)'
        }
    
    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)
        
        # Configuration des champs
        self.fields['quantity'].widget.attrs.update({
            'class': 'form-control',
            'min': '1',
            'step': '1',
            'required': True
        })
        
        # Si c'est une modification, on désactive le type d'opération
        if self.instance and self.instance.pk:
            self.fields['operation_type'].widget.attrs['disabled'] = True
    
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity <= 0:
            raise ValidationError("La quantité doit être supérieure à zéro.")
        return quantity
    
    def clean(self):
        cleaned_data = super().clean()
        operation_type = cleaned_data.get('operation_type')
        quantity = cleaned_data.get('quantity')
        
        # Si c'est un retrait, on vérifie qu'il y a assez de stock
        if operation_type == 'remove' and self.product:
            current_stock = self.product.current_stock
            if quantity > current_stock:
                raise ValidationError({
                    'quantity': f'Stock insuffisant. Quantité disponible : {current_stock}'
                })
        
        # Si c'est un retrait, on convertit la quantité en négatif
        if operation_type == 'remove' and quantity > 0:
            cleaned_data['quantity'] = -quantity
            
        return cleaned_data
