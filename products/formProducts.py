from django import forms
from django.forms import ModelForm, PasswordInput

from products.models import Products


class ProductsFormCreate(forms.ModelForm):
    pass_for_product = forms.CharField(widget=PasswordInput())

    class Meta:
        model = Products
        fields = '__all__'
