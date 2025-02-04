from django import forms
from products.models import GameDetail
class UpdateProductForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        product_id = instance.producto.id_product if instance and instance.producto else None
        license_id = instance.licencia.id_license if instance and instance.licencia else None

        if product_id:
            games_inventory = (GameDetail.objects.filter(producto__id_product=product_id,
                                                licencia__id_license=license_id)
                      .distinct('duracion_dias_alquiler'))
            
            self.fields['licencia'] = forms.ChoiceField(
                choices=[
                    (item.licencia, str(item.licencia))
                    for item in games_inventory
                ],
                widget=forms.Select,
                required=True,
                label="Dias duración"
            )
            
            self.fields['duracion_dias_alquiler'] = forms.ChoiceField(
                choices=[
                    (item.duracion_dias_alquiler, str(item.duracion_dias_alquiler))
                    for item in games_inventory
                ],
                widget=forms.Select,
                required=True,
                label="Dias duración"
            )

    class Meta:
        model = GameDetail
        fields = ('producto','licencia', 'precio', 'duracion_dias_alquiler')