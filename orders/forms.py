from django import forms
from django.core.validators import RegexValidator
from .models import Order

class OrderCreateForm(forms.ModelForm):
    # Ajout d'une validation pour le numéro de téléphone
    phone = forms.CharField(
        label='Téléphone',
        max_length=20,
        validators=[
            RegexValidator(
                regex='^\+?[0-9]{9,15}$',
                message='Entrez un numéro de téléphone valide (9 à 15 chiffres, + optionnel au début)'
            )
        ],
        help_text='Format: 0999999999 ou +243999999999'
    )
    
    # Rendre le champ d'adresse plus convivial
    address = forms.CharField(
        label='Adresse complète',
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Rue, avenue, quartier...'}),
        required=False,
        help_text='Obligatoire pour une livraison à domicile'
    )
    
    class Meta:
        model = Order
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'delivery_type', 'address', 'postal_code', 'city',
            'payment_method', 'notes'
        ]
        widgets = {
            'delivery_type': forms.RadioSelect(choices=Order.DELIVERY_CHOICES),
            'payment_method': forms.RadioSelect(choices=Order.PAYMENT_METHODS),
            'notes': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'Instructions spéciales, informations complémentaires...',
                'class': 'form-control'
            }),
        }
        help_texts = {
            'email': 'Nous vous enverrons la confirmation de commande à cette adresse',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Personnalisation des champs
        self.fields['first_name'].widget.attrs.update({
            'placeholder': 'Votre prénom',
        })
        self.fields['last_name'].widget.attrs.update({
            'placeholder': 'Votre nom',
        })
        self.fields['email'].widget.attrs.update({
            'placeholder': 'votre@email.com',
        })
        self.fields['phone'].widget.attrs.update({
            'placeholder': '0999999999',
        })
        self.fields['city'].widget.attrs.update({
            'placeholder': 'Ville',
        })
        self.fields['postal_code'].widget.attrs.update({
            'placeholder': 'Code postal (optionnel)',
        })
        
        # Ne pas rendre les champs obligatoires ici, on gérera cela dans la méthode clean()
        # pour prendre en compte le type de livraison
        
        # Ajouter des classes Bootstrap aux champs
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.RadioSelect, forms.Textarea)):
                field.widget.attrs.update({'class': 'form-control'})
            if field.required:
                field.widget.attrs['required'] = 'required'
    
    def clean(self):
        cleaned_data = super().clean()
        delivery_type = cleaned_data.get('delivery_type')
        
        # Vérifier que l'adresse est fournie pour une livraison à domicile
        if delivery_type == 'livraison':
            if not cleaned_data.get('address'):
                self.add_error('address', 'Veuillez fournir une adresse de livraison')
            if not cleaned_data.get('city'):
                self.add_error('city', 'Veuillez indiquer la ville de livraison')
            
            # Marquer les champs comme obligatoires pour la validation HTML5
            self.fields['address'].required = True
            self.fields['city'].required = True
            
            # Mettre à jour les attributs required pour la validation côté client
            if 'address' in self.fields:
                self.fields['address'].widget.attrs['required'] = 'required'
            if 'city' in self.fields:
                self.fields['city'].widget.attrs['required'] = 'required'
        else:
            # Pour les autres types de livraison, les champs ne sont pas obligatoires
            if 'address' in self.fields:
                self.fields['address'].required = False
                self.fields['address'].widget.attrs.pop('required', None)
            if 'city' in self.fields:
                self.fields['city'].required = False
                self.fields['city'].widget.attrs.pop('required', None)
        
        # Nettoyer le numéro de téléphone
        phone = cleaned_data.get('phone', '').strip()
        if phone:
            # Supprimer les espaces et les caractères non numériques sauf le + au début
            cleaned_phone = ''.join(c for c in phone if c == '+' or c.isdigit())
            cleaned_data['phone'] = cleaned_phone
        
        return cleaned_data
