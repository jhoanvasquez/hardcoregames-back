from django import forms
from products.models import Products


class ProductsFormCreate(forms.ModelForm):
    class Meta:
        model = Products
        exclude = ['date_last_modified', 'date_register']
