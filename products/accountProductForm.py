from django import forms
from products.models import ProductAccounts


class AccountProductForm(forms.ModelForm):
    class Meta:
        model = ProductAccounts
        # fields = "__all__"
        exclude = [id,]