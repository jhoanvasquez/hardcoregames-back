from django.contrib import admin

from products.formProducts import ProductsFormCreate
from products.models import Products, PaymentType


class ProductsAdmin(admin.ModelAdmin):
    list_display = ['pk','title', 'description', 'stock', 'price', 'email_for_product',
                    'pass_for_product', 'days_enable', 'date_register', 'image', 'date_last_modified',
                    'type_id', 'calification']
    search_fields = ['description', 'calification']
    list_filter = ["days_enable"]
    form = ProductsFormCreate


class PaymentAdmin(admin.ModelAdmin):
    list_display = ['pk', 'description']


# Register your models here.
admin.site.register(Products, ProductsAdmin)
admin.site.register(PaymentType, PaymentAdmin)
