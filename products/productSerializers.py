from rest_framework import serializers

from products.models import Products, ShoppingCar, Licenses, GameDetail, Consoles, SaleDetail


class ProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = (
            'pk', 'title', 'description', 'stock', 'price', 'days_enable', 'date_register', 'image',
            'date_last_modified', 'consola', 'type_id', 'calification')


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = (
            'pk', 'title', 'description', 'stock', 'price', 'days_enable', 'date_register', 'image',
            'date_last_modified', 'consola', 'type_id', 'calification')


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
        fields = ('pk', 'descripcion',)


class SerializerForConsole(serializers.ModelSerializer):
    class Meta:
        model = Consoles
        fields = ('pk', 'descripcion', 'estado')


class SerializerGameDetail(serializers.ModelSerializer):
    desc_licence = serializers.CharField(source='licencia.descripcion', read_only=True)
    desc_console = serializers.CharField(source='consola.descripcion', read_only=True)

    class Meta:
        model = GameDetail
        fields = ('pk', 'consola', 'desc_console', 'licencia', 'desc_licence', 'stock', 'precio')


class SerializerLicencesName(serializers.ModelSerializer):
    desc_licence = serializers.CharField(source='licencia.descripcion', read_only=True)

    class Meta:
        model = GameDetail
        fields = ('licencia', 'desc_licence', 'stock')


class SerializerSales(serializers.ModelSerializer):
    cuenta = serializers.CharField(source='cuenta.cuenta', read_only=True)
    password = serializers.CharField(source='cuenta.password', read_only=True)

    class Meta:
        model = SaleDetail
        fields = ('producto', 'cuenta', 'password', 'fecha_venta', 'fecha_vencimiento')
