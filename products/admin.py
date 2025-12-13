from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Product, Category, Stock
from django.utils import timezone


class StockInline(admin.TabularInline):
    model = Stock
    extra = 1
    fields = ('quantity', 'date_entree', 'notes')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'cement_type', 'price', 'stock_status', 'available')
    list_filter = ('available', 'cement_type', 'category')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [StockInline]
    
    def stock_status(self, obj):
        if obj.stock > 10:
            color = 'green'
        elif obj.stock > 0:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {};">{} en stock</span>',
            color,
            obj.stock
        )
    stock_status.short_description = 'Stock'
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('stock_entries')


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'date_entree', 'created_at')
    list_filter = ('product__category', 'date_entree')
    search_fields = ('product__name', 'notes')
    date_hierarchy = 'date_entree'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only update stock for new entries
            obj.save()  # This will trigger the save method in the model
        else:
            super().save_model(request, obj, form, change)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
