from datetime import date, timedelta

from django.contrib import admin, messages
from django.contrib.admin import SimpleListFilter
from django.urls import reverse
from django.utils.html import format_html

from products.accountProductForm import AccountProductForm
from products.formProducts import ProductsFormCreate
from products.models import Products, PaymentType, ProductsType, Sales, SaleDetail, ProductAccounts
from utils.getJsonFromRequest import GetJsonFromRequest


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
    list_display = ['pk', 'title', 'description', 'stock', 'price', 'email_for_product',
                    'pass_for_product', 'days_enable', 'date_register', 'image', 'date_last_modified',
                    'get_type_product', 'calification']

    list_display_links = ("title",)

    @admin.display(description='Tipo de producto')
    def get_type_product(self, obj):
        return obj.type_id.description

    get_type_product.short_description = 'Tipo de producto'
    search_fields = ['description', 'calification']
    list_filter = ["days_enable", "calification"]
    form = ProductsFormCreate


class PaymentAdmin(admin.ModelAdmin):
    list_display = ['pk', 'description']


class ProductsTypeAdmin(admin.ModelAdmin):
    list_display = ['pk', 'description']


class SalesAdmin(admin.ModelAdmin):
    list_display = ['id_sale', 'date_sale', 'status_sale', 'amount', 'status_sale', 'payment_id', 'user_id']


class ProductAccountsAdmin(admin.ModelAdmin):
    list_display = ['correo', 'password', 'activa', 'producto']
    form = AccountProductForm

    # pass
    def save_model(self, request, obj, form, change):
        email_form = form.cleaned_data.get('correo')
        title_product = form.cleaned_data.get('producto')
        count_account_product = ProductAccounts.objects.filter(correo=email_form).count()
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

    def sale_id(obj):
        url = reverse('admin:products_sales_change', args=[obj.fk_id_sale])
        return format_html(u'<a href="{}" style="margin-right:100px">{}</a>',
                           url, obj.fk_id_sale)

    product_id.short_description = 'Producto'
    sale_id.short_description = 'ID Venta'
    list_display = [field.name for field in SaleDetail._meta.get_fields()]

    list_display.remove("product_id")
    list_display.remove("fk_id_sale")
    list_display += [product_id]
    list_display += [sale_id]
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
admin.site.register(Sales, SalesAdmin)
admin.site.register(SaleDetail, SalesDetailAdmin)
admin.site.register(ProductAccounts, ProductAccountsAdmin)
