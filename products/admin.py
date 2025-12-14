from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Product, Category


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'cement_type', 'price', 'available')
    list_filter = ('available', 'cement_type', 'category')
    search_fields = ('name', 'description', 'cement_type')
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 20
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('stock_entries')




@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
