from django import forms
from products.models import ProductAccounts, Files


class AccountProductForm(forms.ModelForm):
    class Meta:
        model = ProductAccounts
        # fields = "__all__"
        exclude = [id, ]


class FileForm(forms.ModelForm):
    class Meta:
        model = Files
        exclude = ['estado', ]
