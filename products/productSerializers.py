from rest_framework import serializers
from products.models import Products, ShoppingCar, Licenses, Consoles


class ProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = (
            'pk', 'title', 'description', 'stock', 'price', 'days_enable', 'date_register', 'image',
            'date_last_modified',
            'type_id', 'calification', 'combinations_price')


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = (
            'pk', 'title', 'description', 'stock', 'price', 'days_enable', 'date_register', 'image',
            'date_last_modified',
            'type_id', 'calification', 'combinations_price')


class ShoppingCarSerializer(serializers.ModelSerializer):
    id_product = serializers.IntegerField(source='producto.id_product', read_only=True)
    title_product = serializers.CharField(source='producto.title', read_only=True)
    stock = serializers.IntegerField(source='producto.stock', read_only=True)
    price = serializers.IntegerField(source='producto.price', read_only=True)
    type = serializers.IntegerField(source='producto.type_id_id', read_only=True)
    image = serializers.CharField(source='producto.image', read_only=True)

    class Meta:
        model = ShoppingCar
        fields = ('pk', 'id_product', 'title_product', 'stock', 'price', 'type', 'estado', 'image')


class SerializerForTypes(serializers.ModelSerializer):
    class Meta:
        model = Licenses
        fields = ('pk', 'descripcion')
