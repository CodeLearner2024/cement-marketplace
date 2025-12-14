from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0
    readonly_fields = ['get_cost']
    
    def get_cost(self, obj):
        return f"{obj.get_cost():.2f} €"
    get_cost.short_description = 'Total'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'first_name', 'last_name', 'email', 
        'delivery_type', 'total_amount_display', 'payment_method', 
        'status', 'created_at', 'updated_at', 'order_actions'
    ]
    list_filter = ['status', 'delivery_type', 'payment_method', 'created_at', 'updated_at']
    search_fields = ['first_name', 'last_name', 'email', 'id', 'phone']
    inlines = [OrderItemInline]
    readonly_fields = ['created_at', 'updated_at', 'user', 'total_amount']
    list_per_page = 20
    date_hierarchy = 'created_at'
    
    fieldsets = [
        ('Informations client', {
            'fields': [
                'user', 'first_name', 'last_name', 'email', 'phone'
            ]
        }),
        ('Détails de la commande', {
            'fields': [
                'status', 'delivery_type', 'payment_method', 'total_amount',
                'address', 'postal_code', 'city', 'notes', 'paid'
            ]
        }),
        ('Dates', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    
    def total_amount_display(self, obj):
        return f"{obj.total_amount:.2f} €"
    total_amount_display.short_description = 'Montant total'
    
    def order_actions(self, obj):
        return format_html(
            '<a class="button" href="{}">Voir</a>',
            f'/admin/orders/order/{obj.id}/change/'
        )
    order_actions.short_description = 'Actions'
    order_actions.allow_tags = True


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_link', 'product', 'price_display', 'quantity', 'get_cost']
    list_select_related = ['order', 'product']
    search_fields = ['order__id', 'product__name']
    list_filter = ['order__status', 'order__delivery_type']
    list_per_page = 20
    raw_id_fields = ['order', 'product']
    
    def order_link(self, obj):
        return format_html(
            '<a href="{}">Commande #{}</a>',
            f'/admin/orders/order/{obj.order.id}/change/',
            obj.order.id
        )
    order_link.short_description = 'Commande'
    order_link.admin_order_field = 'order__id'
    
    def price_display(self, obj):
        return f"{obj.price:.2f} €"
    price_display.short_description = 'Prix unitaire'
    
    def get_cost(self, obj):
        return f"{obj.get_cost():.2f} €"
    get_cost.short_description = 'Total'
