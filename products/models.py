from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now


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


class Products(models.Model):
    id_product = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200, default="")
    description = models.TextField()
    stock = models.IntegerField(default=0)
    price = models.IntegerField()
    date_register = models.DateField(default=datetime.now)
    date_last_modified = models.DateField(auto_now=True)
    image = models.CharField(max_length=500)
    type_id = models.ForeignKey(ProductsType, on_delete=models.CASCADE)
    calification = models.IntegerField(default=0)
    consola = models.ManyToManyField(Consoles)
    tipo_juego = models.ForeignKey(TypeGames, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'un producto'
        verbose_name_plural = 'Productos'


class ProductAccounts(models.Model):
    id_product_accounts = models.AutoField(primary_key=True)
    cuenta = models.CharField(max_length=200)
    password = models.CharField(max_length=100, null=True)
    activa = models.BooleanField()
    producto = models.ForeignKey(Products, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'una cuenta para producto'
        verbose_name_plural = 'Cuentas para productos'

    def __str__(self):
        return self.cuenta


class SaleDetail(models.Model):
    id_sale_detail = models.AutoField(primary_key=True)
    fecha_venta = models.DateField(default=datetime.now)
    fecha_vencimiento = models.DateField(null=True)
    cuenta = models.ForeignKey(ProductAccounts, on_delete=models.CASCADE, null=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    producto = models.ForeignKey(Products, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = 'un detalle de venta'
        verbose_name_plural = 'Detalle de ventas'

    def __str__(self):
        return "Detalle de venta para la cuenta " + self.cuenta.cuenta


class Licenses(models.Model):
    id_license = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=100)

    def __str__(self):
        return self.descripcion

    def get_id_licence(self):
        return self.id_license


class GameDetail(models.Model):
    id_game_detail = models.AutoField(primary_key=True)
    producto = models.ForeignKey(Products, on_delete=models.CASCADE, null=True)
    consola = models.ForeignKey(Consoles, on_delete=models.CASCADE, null=True)
    licencia = models.ForeignKey(Licenses, on_delete=models.CASCADE, null=True)
    stock = models.IntegerField()
    precio = models.IntegerField(default=0)
    estado = models.BooleanField()

    class Meta:
        verbose_name = 'Precio por consola y licencia'
        verbose_name_plural = 'Precios por consola y licencia'


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
