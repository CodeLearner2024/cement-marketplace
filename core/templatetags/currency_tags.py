from django import template
from decimal import Decimal

register = template.Library()

@register.filter(name='currency')
def currency(value):
    """
    Format a decimal value as BIF currency.
    Example: {{ value|currency }}
    """
    if value is None or value == '':
        return "0 BIF"
    try:
        # Convertir en décimal si ce n'est pas déjà le cas
        decimal_value = Decimal(str(value))
        # Formater avec 2 décimales et le symbole BIF
        return f"{decimal_value:,.2f} BIF"
    except (ValueError, TypeError):
        return f"{value} BIF"  # En cas d'erreur, on affiche la valeur telle quelle avec BIF
