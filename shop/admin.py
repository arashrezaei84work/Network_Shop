from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title',)
    exclude = ('slug',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'price','stock' , 'is_available')
    list_filter = ('category', 'is_available')
    search_fields = ('name', 'brand')
    # exclude = ('slug',)
