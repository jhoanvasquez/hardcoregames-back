from rest_framework import serializers

from products.models import Products, ShoppingCar, Licenses, GameDetail, Consoles, SaleDetail, DaysForRentail, \
    PriceForSuscription


class SerializerForConsole(serializers.ModelSerializer):
    class Meta:
        model = Consoles
        fields = ('pk', 'descripcion', 'estado')


class ProductsSerializer(serializers.ModelSerializer):
    consola = SerializerForConsole(read_only=True, many=True)

    class Meta:
        model = Products
        fields = (
            'pk', 'title', 'description', 'stock', 'price', 'date_register', 'image',
            'date_last_modified', 'consola', 'type_id', 'calification', 'tipo_juego', 'puntos_venta', 'puede_rentarse')


class ProductSerializer(serializers.ModelSerializer):
    consola = SerializerForConsole(read_only=True, many=True)

    class Meta:
        model = Products
        fields = (
            'pk', 'title', 'description', 'stock', 'price', 'date_register', 'image',
            'date_last_modified', 'consola', 'type_id', 'calification', 'tipo_juego', 'puntos_venta', 'puede_rentarse')


class ShoppingCarSerializer(serializers.ModelSerializer):
    id_product = serializers.IntegerField(source='producto.producto.id_product', read_only=True)
    id_combination = serializers.IntegerField(source='producto.id_game_detail', read_only=True)
    title_product = serializers.CharField(source='producto.producto.title', read_only=True)
    stock = serializers.IntegerField(source='producto.stock', read_only=True)
    licence = serializers.CharField(source='producto.licencia.descripcion', read_only=True)
    console = serializers.CharField(source='producto.consola.descripcion', read_only=True)
    price = serializers.IntegerField(source='producto.precio', read_only=True)
    type = serializers.IntegerField(source='producto.producto.type_id_id', read_only=True)
    image = serializers.CharField(source='producto.producto.image', read_only=True)

    class Meta:
        model = ShoppingCar
        fields = ('pk', 'id_product', 'id_combination', 'title_product', 'stock', 'price', 'licence', 'console',
                  'type', 'estado', 'image')


class SerializerForTypes(serializers.ModelSerializer):
    class Meta:
        model = Licenses
        fields = ('pk', 'descripcion',)


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


class SerializerPriceSuscriptionProduct(serializers.ModelSerializer):
    class Meta:
        model = PriceForSuscription
        fields = ('tiempo_alquiler', 'precio')


class SerializerDaysForRentail(serializers.ModelSerializer):
    class Meta:
        model = DaysForRentail
        fields = ('pk', 'numero_dias', 'porcentaje_descuento')


class SerializerSales(serializers.ModelSerializer):
    cuenta = serializers.CharField(source='cuenta.cuenta', read_only=True)
    password = serializers.CharField(source='cuenta.password', read_only=True)
    productName = serializers.CharField(source='producto.title', read_only=True)
    productImage = serializers.CharField(source='producto.image', read_only=True)

    class Meta:
        model = SaleDetail
        fields = ('producto', 'cuenta', 'productName', 'productImage', 'password', 'fecha_venta', 'fecha_vencimiento')
