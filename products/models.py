from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now


# Create your models here.
class ProductsType(models.Model):
    id_product_type = models.AutoField(primary_key=True)
    description = models.CharField(max_length=200)


class PaymentType(models.Model):
    id_payment_type = models.AutoField(primary_key=True)
    description = models.CharField(max_length=200)

class Products(models.Model):
    id_product = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200, default="")
    description = models.CharField(max_length=200)
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

class Sales(models.Model):
    id_sale = models.AutoField(primary_key=True)
    description = models.CharField(max_length=200)
    status_sale = models.CharField(max_length=10)
    date_sale = models.DateField()
    last_modified = models.DateField()
    payment_id = models.ForeignKey(PaymentType, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
