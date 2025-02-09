import glob
import os
from datetime import date, timedelta
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin import SimpleListFilter
from django.core.cache import cache
from django.db import models
from django.db.models import F, Sum, Count, Q
from django.forms import Textarea
from django.urls import reverse
from django.utils.html import format_html
from django.shortcuts import redirect
from django.db import connection

from products.accountProductForm import AccountProductForm, FileForm
from products.formProducts import ProductsFormCreate
from products.managePriceFile import ManegePricesFile
from products.models import Products, ProductsType, SaleDetail, ProductAccounts, Files, GameDetail, Consoles, \
    TypeGames, VariablesSistema, Licenses, TypeAccounts

from products.UpdateProductForm import UpdateProductForm
@admin.action(description="Update price and other fields")
def update_game_detail(admin_model, request, queryset):
    if 'apply' in request.POST:
        product = request.POST.get('producto')
        console = request.POST.get('consola')
        licencia = request.POST.get('licencia')
        new_price = request.POST.get('precio')

        # Filter and update the GameDetail objects based on producto, consola, and licencia
        game_details = queryset.filter(
            producto=product,
            consola=console,
            licencia=licencia
        )

        updated_count = game_details.update(
            precio=new_price,
        )
        messages.success(request, f"Successfully updated {updated_count} game details.")
        return None


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
            return queryset.filter(fecha_vencimiento__range=(today, today + timedelta(days=int(self.value()))))


class ProductsAdmin(admin.ModelAdmin):

    list_display = ('id_product','title','stock_primaries', 'price_primaries',
                    'stock_secondaries', 'price_secondaries',
                    'stock_codes', 'price_codes',
                    'stock_pc', 'price_pc', 'console', 'duration_days')

    @staticmethod
    def product_id(obj):
        price_codes = (
            GameDetail.objects.filter(
                licencia__id_license=1,
                producto__id_product=obj.id_product,
                stock__gt = 0
            )
            .first())
        return price_codes.id_game_detail if price_codes is not None else None

    @staticmethod
    def stock_primaries(obj):
        return (
                GameDetail.objects.filter(
                    licencia__id_license=1,
                    producto__id_product=obj.id_product,
                    stock__gt = 0
                )
                .aggregate(total_stock=Sum('stock'))['total_stock'] or 0)

    @staticmethod
    def stock_secondaries(obj):
        return (
                GameDetail.objects.filter(
                    licencia__id_license=2,
                    producto__id_product=obj.id_product,
                    stock__gt = 0
                )
                .aggregate(total_stock=Sum('stock'))['total_stock'] or 0
        )

    @staticmethod
    def stock_codes(obj):
        return (
                GameDetail.objects.filter(
                    licencia__id_license=3,
                    producto__id_product=obj.id_product
                )
                .aggregate(total_stock=Sum('stock'))['total_stock'] or 0
        )


    @staticmethod
    def stock_pc(obj):
        return (
                GameDetail.objects.filter(
                    licencia__id_license=4,
                    producto__id_product=obj.id_product,
                )
                .aggregate(total_stock=Sum('stock'))['total_stock'] or 0
        )

    @staticmethod
    def price_primaries(obj):
        inventory_primary = (
            GameDetail.objects.filter(
                licencia__id_license=1,
                producto__id_product=obj.id_product
            ).first()
        )
        if inventory_primary is None:
            return None
        url = f"/admin/products/gamedetail/{inventory_primary.id_game_detail}/change/"
        return format_html(
            '<a href="{}" target="_blank">{}</a>',
            url,
            inventory_primary.precio
        )

    @staticmethod
    def price_secondaries(obj):
        inventory_secondary = (
            GameDetail.objects.filter(
                licencia__id_license=2,
                producto__id_product=obj.id_product
            ).first()
        )
        if inventory_secondary is None:
            return None
        url = f"/admin/products/gamedetail/{inventory_secondary.id_game_detail}/change/"
        return format_html(
            '<a href="{}" target="_blank">{}</a>',
            url,
            inventory_secondary.precio
        )
    @staticmethod
    def price_codes(obj):
        inventory_codes = (
            GameDetail.objects.filter(
                licencia__id_license=3,
                producto__id_product=obj.id_product
            ).first()
        )
        if inventory_codes is None:
            return None
        url = f"/admin/products/gamedetail/{inventory_codes.id_game_detail}/change/"
        return format_html(
            '<a href="{}" target="_blank">{}</a>',
            url,
            inventory_codes.precio
        )

    @staticmethod
    def price_pc(obj):
        inventory_pc = (
            GameDetail.objects.filter(
                licencia__id_license=4,
                producto__id_product=obj.id_product
            ).first()
        )
        if inventory_pc is None:
            return None
        url = f"/admin/products/gamedetail/{inventory_pc.id_game_detail}/change/"
        return format_html(
            '<a href="{}" target="_blank">{}</a>',
            url,
            inventory_pc.precio
        )

    @staticmethod
    def console(obj):
        game_inventory = (
            GameDetail.objects.filter(
                producto__id_product=obj.id_product
            ).distinct('consola')
        )
        return ", ".join(str(result.consola) for result in game_inventory) \
            if game_inventory is not None else None

    @staticmethod
    def duration_days(obj):
        game_inventory = (
            GameDetail.objects.filter(
                producto__id_product=obj.id_product
            ).distinct('duracion_dias_alquiler')
        )
        return ", ".join(str(result.duracion_dias_alquiler) for result in game_inventory) \
            if game_inventory is not None else None
    list_per_page = 5
    search_fields = ['title',]
    list_filter = ["consola",]

class PaymentAdmin(admin.ModelAdmin):
    list_display = ['pk', 'description']


class ProductsTypeAdmin(admin.ModelAdmin):
    list_display = ['pk', 'description']


class ConsolesAdmin(admin.ModelAdmin):
    list_display = ['pk', 'descripcion', 'estado']
    search_fields = ['producto__title',]

class TypeGamesAdmin(admin.ModelAdmin):
    list_display = ['id_type_game', 'descripcion']


class TypeAccountsAdmin(admin.ModelAdmin):
    list_display = ['id_type_account', 'descripcion']


class LicencesAdmin(admin.ModelAdmin):
    list_display = ['id_license', 'descripcion']

class GameDetailAdmin(admin.ModelAdmin):
    @staticmethod
    def has_module_permission(request):
        return False
    def product(obj):
        url = reverse('admin:products_products_change', args=[obj.producto.id_product])
        return format_html(u'<a href="{}" style="margin-right:100px">{}</a>',
                           url, obj.producto.title)

    def save_model(self, request, obj, form, change):

        super(GameDetailAdmin, self).save_model(request, obj, form, change)
        product = int(request.POST.get('producto'))
        license = int(request.POST.get('licencia'))
        duration_days = int(request.POST.get('duracion_dias_alquiler'))

        game_details = GameDetail.objects.filter(
            producto=product,
            licencia=license,
            duracion_dias_alquiler=duration_days
        ).values('producto', 'duracion_dias_alquiler', 'precio')

        if request.POST.get('price_type') == '1':
            new_price = request.POST.get('precio_descuento')
            game_details.update(precio_descuento=new_price)
        else:
            new_price = request.POST.get('precio')
            game_details.update(precio=new_price)

        messages.success(request, f"Successfully updated game details.")
        return None

    @staticmethod
    def response_change(request, obj):
        return redirect('/admin/products/products/')

    product.short_description = 'Producto'
    search_fields = ['producto__title', 'producto__id_product', 'cuenta__cuenta']
    list_filter = ["consola", 'licencia']
    form = UpdateProductForm
    list_display = ('consola', 'licencia', 'precio')  # Display in the admin list view
    actions = [update_game_detail]
    list_per_page = 10

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


class SystemVariablesAdmin(admin.ModelAdmin):
    list_display = ['nombre_variable', 'descripcion', 'valor', 'url', 'estado']


class ProductAccountsAdmin(admin.ModelAdmin):
    list_display = ['cuenta', 'password', 'activa', 'tipo_cuenta', 'dias_duracion', 'codigo_seguridad', ]
    form = AccountProductForm
    search_fields = ['cuenta','producto__title', 'producto__id_product']
    list_filter = ["tipo_cuenta",]
    list_per_page = 10

class SalesDetailAdmin(admin.ModelAdmin):
    def producto(obj):
        url = reverse('admin:products_products_change', args=[obj.producto.id_product])
        return format_html(u'<a href="{}" style="margin-right:100px">{}</a>',
                           url, obj.producto.title)

    def cuenta(obj):
        url = reverse('admin:products_productaccounts_change', args=[obj.cuenta.id_product_accounts])
        return format_html(u'<a href="{}" style="margin-right:100px">{}</a>',
                           url, obj.cuenta.cuenta)

    def password(self, obj):
        return obj.cuenta.password

    list_display = ["pk", producto, "combinacion", "fecha_venta", "fecha_vencimiento", cuenta,
                    "password", "usuario"]
    list_filter = [CloseToExp]

    @admin.action(description='Enviar mensaje de renovación')
    def send_email_renovation(self, request, queryset):
        for sale in queryset:
            print(sale)
        messages.add_message(request, messages.INFO, 'Mensaje enviado exitosamente')

    actions = [send_email_renovation]
    search_fields = ["usuario__email", ]
    list_per_page = 10

admin.site.site_header = 'Administración HardCoreGames'
# Register your models here.
admin.site.register(Products, ProductsAdmin)
admin.site.register(ProductsType, ProductsTypeAdmin)
admin.site.register(SaleDetail, SalesDetailAdmin)
admin.site.register(ProductAccounts, ProductAccountsAdmin)
admin.site.register(Consoles, ConsolesAdmin)
admin.site.register(GameDetail, GameDetailAdmin)
admin.site.register(Files, FilesAdmin)
admin.site.register(TypeGames, TypeGamesAdmin)
admin.site.register(TypeAccounts, TypeAccountsAdmin)
admin.site.register(VariablesSistema, SystemVariablesAdmin)
admin.site.register(Licenses, LicencesAdmin)
