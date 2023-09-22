from django.contrib import admin

from products.formProducts import ProductsFormCreate
from products.models import Products


class ProductsAdmin(admin.ModelAdmin):
    form = ProductsFormCreate


# Register your models here.
admin.site.register(Products, ProductsAdmin)
