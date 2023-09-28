from rest_framework import serializers
from products.models import Products


class ProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ('pk', 'title', 'description', 'stock', 'price', 'email_for_product',
                  'pass_for_product', 'days_enable', 'date_register', 'image', 'date_last_modified',
                  'type_id', 'calification')


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ('pk', 'title', 'description', 'stock', 'price', 'email_for_product',
                  'pass_for_product', 'days_enable', 'date_register', 'image', 'date_last_modified',
                  'type_id', 'calification')
