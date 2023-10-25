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


class PaymentType(models.Model):
    id_payment_type = models.AutoField(primary_key=True)
    description = models.CharField(max_length=200)

    def __str__(self):
        return self.description


class Products(models.Model):
    id_product = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200, default="")
    description = models.TextField()
    stock = models.IntegerField()
    price = models.IntegerField()
    email_for_product = models.EmailField(max_length=100)
    pass_for_product = models.CharField(max_length=100)
    days_enable = models.IntegerField()
    date_register = models.DateField(default=now)
    date_last_modified = models.DateField(default=now)
    image = models.CharField(max_length=500)
    type_id = models.ForeignKey(ProductsType, on_delete=models.CASCADE)
    calification = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'un producto'
        verbose_name_plural = 'Productos'


class Sales(models.Model):
    id_sale = models.AutoField(primary_key=True)
    date_sale = models.DateField()
    status_sale = models.CharField(max_length=10)
    amount = models.IntegerField(default=0)
    payment_id = models.ForeignKey(PaymentType, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'una venta'
        verbose_name_plural = 'Ventas'

    def __str__(self):
        return str(self.id_sale)


class SaleDetail(models.Model):
    id_sale_detail = models.AutoField(primary_key=True)
    price = models.IntegerField()
    quantity = models.IntegerField()
    total_value = models.IntegerField(default=0)
    date_expiration = models.DateField(null=True)
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE)
    fk_id_sale = models.ForeignKey(Sales, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = 'una detalle de venta'
        verbose_name_plural = 'Detalle de ventas'

    def __str__(self):
        return "Detalle de venta para producto " + self.product_id.title

class ProductAccounts(models.Model):
    id_product_accounts = models.AutoField(primary_key=True)
    correo = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    activa = models.BooleanField()
    producto = models.ForeignKey(Products, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'una cuenta para producto'
        verbose_name_plural = 'Cuentas para productos'

    def __str__(self):
        return "Cuenta: "+self.correo+" para producto " + self.producto.title