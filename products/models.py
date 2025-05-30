from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class ProductsType(models.Model):
    id_product_type = models.AutoField(primary_key=True)
    description = models.CharField(max_length=200)

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = 'un tipo de producto'
        verbose_name_plural = 'Tipos de producto'


class Consoles(models.Model):
    id_console = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=100)
    estado = models.BooleanField(null=True)

    def __str__(self):
        return self.descripcion

    def get_id_console(self):
        return self.id_console

    class Meta:
        verbose_name = 'una consola'
        verbose_name_plural = 'Consolas'


class TypeGames(models.Model):
    id_type_game = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=100)

    def __str__(self):
        return self.descripcion

    class Meta:
        verbose_name = 'una tipo de juego'
        verbose_name_plural = 'Tipos de juegos'


class Products(models.Model):
    id_product = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200, default="")
    description = models.TextField()
    date_register = models.DateField(default=datetime.now)
    date_last_modified = models.DateField(auto_now=True)
    image = models.CharField(max_length=500)
    type_id = models.ForeignKey(ProductsType, on_delete=models.CASCADE)
    calification = models.IntegerField(default=0)
    consola = models.ManyToManyField(Consoles)
    tipo_juego = models.ForeignKey(TypeGames, on_delete=models.CASCADE, null=True, blank=True)
    puntos_venta = models.IntegerField(default=0)
    puede_rentarse = models.BooleanField(default=True)
    destacado = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id_product) + " " + str(self.title)

    class Meta:
        verbose_name = 'un producto'
        verbose_name_plural = 'Productos'


class TypeAccounts(models.Model):
    id_type_account = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=100)

    def __str__(self):
        return self.descripcion

    class Meta:
        verbose_name = 'Tipo cuenta'
        verbose_name_plural = 'Tipos de cuentas'


class TypeSuscriptionAccounts(models.Model):
    id_type_suscription_account = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=100)

    def __str__(self):
        return self.descripcion

    class Meta:
        verbose_name = 'Tipo cuenta suscripcion'
        verbose_name_plural = 'Tipos de cuentas suscripcion'


class ProductAccounts(models.Model):
    id_product_accounts = models.AutoField(primary_key=True)
    cuenta = models.CharField(max_length=200)
    password = models.CharField(max_length=100, null=True, blank=True)
    activa = models.BooleanField()
    tipo_cuenta = models.ForeignKey(TypeAccounts, on_delete=models.CASCADE, default=1)
    dias_duracion = models.IntegerField(default=0, null=True, blank=True)
    codigo_seguridad = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        verbose_name = 'una cuenta para producto'
        verbose_name_plural = 'Cuentas para productos'

    def __str__(self):
        return self.cuenta


class Licenses(models.Model):
    id_license = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=100)

    def __str__(self):
        return self.descripcion

    def get_id_licence(self):
        return self.id_license

    class Meta:
        verbose_name = 'Licencia'
        verbose_name_plural = 'Licencias'


class GameDetail(models.Model):
    id_game_detail = models.AutoField(primary_key=True)
    producto = models.ForeignKey(Products, on_delete=models.CASCADE, null=True)
    consola = models.ForeignKey(Consoles, on_delete=models.CASCADE, null=True)
    licencia = models.ForeignKey(Licenses, on_delete=models.CASCADE, null=True)
    cuenta = models.ForeignKey(ProductAccounts, on_delete=models.CASCADE, null=True)
    duracion_dias_alquiler = models.IntegerField(null=True)
    stock = models.IntegerField()
    precio = models.IntegerField(default=0)
    precio_descuento = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Precio por consola y licencia'
        verbose_name_plural = 'Precios por consola y licencia'

    def __str__(self):
        return str(self.consola) + " " + str(self.licencia)


class SaleDetail(models.Model):
    id_sale_detail = models.AutoField(primary_key=True)
    fecha_venta = models.DateTimeField(default=datetime.now, blank=True)
    fecha_vencimiento = models.DateField(null=True)
    cuenta = models.ForeignKey(ProductAccounts, on_delete=models.CASCADE, null=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    producto = models.ForeignKey(Products, on_delete=models.CASCADE, null=True)
    combinacion = models.ForeignKey(GameDetail, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = 'un detalle de venta'
        verbose_name_plural = 'Detalle de ventas'

    def __str__(self):
        return "Detalle de venta para la cuenta " + self.cuenta.cuenta


class ShoppingCar(models.Model):
    id_shopping_car = models.AutoField(primary_key=True)
    producto = models.ForeignKey(GameDetail, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    estado = models.BooleanField()

    # def __str__(self):
    #     return "Detalle de venta para la cuenta " + self.cuenta.cuenta


class Files(models.Model):
    id_file = models.AutoField(primary_key=True)
    archivo = models.FileField(upload_to=settings.STATIC_URL_FILES)
    estado = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'un archivo para precios'
        verbose_name_plural = 'Archivos para precios'


class DaysForRentail(models.Model):
    id_day = models.AutoField(primary_key=True)
    numero_dias = models.CharField(max_length=100)
    porcentaje_descuento = models.CharField(max_length=100)

    def __str__(self):
        return self.numero_dias

    class Meta:
        verbose_name = 'valor descuento por mes'
        verbose_name_plural = 'Meses para alquiler'


class PriceForSuscription(models.Model):
    id_price_suscription = models.AutoField(primary_key=True)
    producto = models.ForeignKey(Products, on_delete=models.CASCADE, null=True)
    tipo_producto = models.ForeignKey(TypeSuscriptionAccounts, on_delete=models.CASCADE)
    tiempo_alquiler = models.CharField(max_length=100, default="")
    stock = models.IntegerField(default=0)
    duracion_dias_alquiler = models.IntegerField(default=0)
    precio = models.IntegerField()
    estado = models.BooleanField(default=True)

    def __str__(self):
        return str(self.producto.id_product) + " " + str(self.producto.title)

    class Meta:
        verbose_name = 'precio producto suscripción'
        verbose_name_plural = 'Precio producto suscripción'


class VariablesSistema(models.Model):
    id_vairables_sistema = models.AutoField(primary_key=True)
    nombre_variable = models.CharField(max_length=100)
    descripcion = models.TextField(null=True, default=None, blank=True)
    valor = models.CharField(max_length=500)
    url = models.TextField(null=True, default=None, blank=True)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return str(self.nombre_variable)

    class Meta:
        verbose_name = 'variable de sistema'
        verbose_name_plural = 'Variables de sistema'

class Transactions(models.Model):
    id_transaction = models.AutoField(primary_key=True)
    date_transaction = models.DateTimeField(default=datetime.now, blank=True)
    status = models.CharField(max_length=100)
    amount = models.IntegerField()
    payment_id = models.CharField(max_length=100)
    ref_payco = models.CharField(max_length=100)
    id_invoice = models.CharField(max_length=100)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)