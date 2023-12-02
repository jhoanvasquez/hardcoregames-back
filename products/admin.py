import glob
import os
from datetime import date, timedelta

from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin import SimpleListFilter
from django.db import models
from django.forms import Textarea
from django.urls import reverse
from django.utils.html import format_html
from django.utils.text import Truncator

from products.accountProductForm import AccountProductForm, FileForm
from products.formProducts import ProductsFormCreate
from products.managePriceFile import ManegePricesFile
from products.models import Products, ProductsType, SaleDetail, ProductAccounts, Files, GameDetail, Consoles, \
    DaysForRentail, TypeGames


class CloseToExp(SimpleListFilter):
    title = "proximos a vencer"  # a label for our filter
    parameter_name = "days"  # you can put anything here

    def lookups(self, request, model_admin):
        return [
            ("5", "5 dias"),
            ("15", "15 dias"),
        ]

    def queryset(self, request, queryset):
        if self.value():
            today = date.today()
            return queryset.filter(date_expiration__range=(today, today + timedelta(days=int(self.value()))))


class ProductsAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 4})},
    }

    list_display = ['pk', 'title', 'stock', 'price', 'nombre_consola', 'image',
                    'get_type_product', 'tipo_juego', 'calification']

    list_display_links = ("title",)
    filter_horizontal = ('consola',)

    def nombre_consola(self, obj):
        return [console.descripcion for console in obj.consola.all()]

    @admin.display(description='Tipo de producto')
    def get_type_product(self, obj):
        return obj.type_id.description

    get_type_product.short_description = 'Tipo de producto'
    search_fields = ['title', 'description', 'calification']
    list_filter = ["calification", 'tipo_juego']
    form = ProductsFormCreate


class PaymentAdmin(admin.ModelAdmin):
    list_display = ['pk', 'description']


class ProductsTypeAdmin(admin.ModelAdmin):
    list_display = ['pk', 'description']


class ConsolesAdmin(admin.ModelAdmin):
    list_display = ['pk', 'descripcion', 'estado']


class DaysForRentailAdmin(admin.ModelAdmin):
    list_display = ['pk', 'numero_dias', 'porcentaje_descuento']


class TypeGamesAdmin(admin.ModelAdmin):
    list_display = ['descripcion']


class GameDetailAdmin(admin.ModelAdmin):
    def product(obj):
        url = reverse('admin:products_products_change', args=[obj.producto.id_product])
        return format_html(u'<a href="{}" style="margin-right:100px">{}</a>',
                           url, obj.producto.title)

    product.short_description = 'Producto'
    list_display = [product, 'consola', 'licencia', 'stock', 'precio']
    list_filter = ["consola", 'licencia']


class SalesAdmin(admin.ModelAdmin):
    list_display = ['id_sale', 'date_sale', 'status_sale', 'amount', 'status_sale', 'payment_id', 'user_id']


class FilesAdmin(admin.ModelAdmin):
    list_display = ['archivo']
    form = FileForm

    def save_model(self, request, obj, form, change):
        for filename in glob.glob(settings.STATIC_URL_FILES + '*.xlsx'):
            os.remove(filename)
        Files.objects.all().delete()
        super(FilesAdmin, self).save_model(request, obj, form, change)
        ManegePricesFile()


class ProductAccountsAdmin(admin.ModelAdmin):
    list_display = ['cuenta', 'password', 'activa', 'producto']
    form = AccountProductForm

    def save_model(self, request, obj, form, change):
        email_form = form.cleaned_data.get('cuenta')
        title_product = form.cleaned_data.get('producto')
        count_account_product = ProductAccounts.objects.filter(cuenta=email_form).count()
        stock_product = Products.objects.filter(title=title_product).values("stock")[0]['stock']
        if int(stock_product) >= count_account_product:
            super(ProductAccountsAdmin, self).save_model(request, obj, form, change)
        else:
            messages.set_level(request, messages.ERROR)
            messages.error(request, "El número de cuentas para este producto ha excedido el stock")


class SalesDetailAdmin(admin.ModelAdmin):
    def product_id(obj):
        url = reverse('admin:products_products_change', args=[obj.product_id.id_product])
        return format_html(u'<a href="{}" style="margin-right:100px">{}</a>',
                           url, obj.product_id.title)

    def cuenta(obj):
        url = reverse('admin:products_productaccounts_change', args=[obj.cuenta.id_product_accounts])
        return format_html(u'<a href="{}" style="margin-right:100px">{}</a>',
                           url, obj.cuenta.cuenta)

    product_id.short_description = 'Producto'
    list_display = [field.name for field in SaleDetail._meta.get_fields()]

    list_display.remove("cuenta")
    list_display += [cuenta]
    list_filter = [CloseToExp]

    # list_display_links = ("id_sale", product_id)

    @admin.action(description='Enviar mensaje de renovación')
    def send_email_renovation(self, request, queryset):
        for sale in queryset:
            print(sale)
        messages.add_message(request, messages.INFO, 'Mensaje enviado exitosamente')

    actions = [send_email_renovation]


admin.site.site_header = 'Administración HardCoreGames'
# Register your models here.
admin.site.register(Products, ProductsAdmin)
admin.site.register(ProductsType, ProductsTypeAdmin)
admin.site.register(SaleDetail, SalesDetailAdmin)
admin.site.register(ProductAccounts, ProductAccountsAdmin)
admin.site.register(Consoles, ConsolesAdmin)
admin.site.register(GameDetail, GameDetailAdmin)
admin.site.register(Files, FilesAdmin)
admin.site.register(DaysForRentail, DaysForRentailAdmin)
admin.site.register(TypeGames, TypeGamesAdmin)
