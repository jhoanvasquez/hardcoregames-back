from django.contrib.auth.models import User
from django.db import models


class TypeDocument(models.Model):
    type_id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=200)


class User_Customized(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id_document = models.IntegerField(default=1)
    phone_number = models.CharField(max_length=20)
    avatar = models.CharField(max_length=500, default="")
    type_id_document = models.ForeignKey(TypeDocument, default=1, on_delete=models.CASCADE)
    puntos = models.IntegerField(default=0)