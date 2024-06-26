import glob
import os

import openpyxl
from django import forms
from django.conf import settings
from django.db.models import F

from products.UpdateStock import UpdateStock
from products.models import ProductAccounts, Consoles, Licenses, Products, GameDetail, TypeAccounts, \
    PriceForSuscription, TypeSuscriptionAccounts


def read_file_ps(sheetPs, id_primaria, id_secundaria):
    id_ps4 = Consoles.objects.filter(descripcion__icontains="playstation 4")
    id_ps5 = Consoles.objects.filter(descripcion__icontains="playstation 5")
    is_new_account = False
    # try:
    sheet = sheetPs
    m_row = sheet.max_row

    for i in range(2, m_row + 1):
        account = sheet.cell(row=i, column=1).value
        password = sheet.cell(row=i, column=2).value
        id_product = sheet.cell(row=i, column=3).value
        product_for_create = Products.objects.filter(id_product=id_product)
        duration_days = sheet.cell(row=i, column=8).value
        type_account = sheet.cell(row=i, column=9).value

        if account is None or id_product is None:
            continue

        if not product_for_create.exists():
            raise forms.ValidationError(u"el producto para play station con id " + str(id_product) + " no existe")

        exist_account = ProductAccounts.objects.filter(cuenta=account.lower(),
                                                       producto=int(id_product)).exists()

        type_account = 1 if type_account is None else type_account
        type_account_selected = TypeAccounts.objects.filter(pk=type_account)
        duration_days = 0 if duration_days is None else duration_days
        if not exist_account:
            ProductAccounts(
                cuenta=account.lower(),
                password=password,
                activa=True,
                producto=product_for_create.first(),
                tipo_cuenta=type_account_selected.first(),
                dias_duracion=duration_days
            ).save()
            is_new_account = True
        sheet_price_ps4_1 = str(sheet.cell(row=i, column=4).value).strip()
        sheet_price_ps4_2 = str(sheet.cell(row=i, column=5).value).strip()
        sheet_price_ps5_1 = str(sheet.cell(row=i, column=6).value).strip()
        sheet_price_ps5_2 = str(sheet.cell(row=i, column=7).value).strip()

        if check_sheet_price(sheet_price_ps4_1):
            save_or_update_game_detail(id_product, id_ps4, id_primaria, sheet_price_ps4_1, is_new_account, duration_days)
        if check_sheet_price(sheet_price_ps4_2):
            save_or_update_game_detail(id_product, id_ps4, id_secundaria, sheet_price_ps4_2, is_new_account, duration_days)
        if check_sheet_price(sheet_price_ps5_1):
            save_or_update_game_detail(id_product, id_ps5, id_primaria, sheet_price_ps5_1, is_new_account, duration_days)
        if check_sheet_price(sheet_price_ps5_2):
            save_or_update_game_detail(id_product, id_ps5, id_secundaria, sheet_price_ps5_2, is_new_account, duration_days)

    # except Exception as e:
    #     print("problemas en el manejo del archivo cuentas play station " + str(e))


def read_file_xbx(sheetPs, id_primaria, id_secundaria):
    id_xbox = Consoles.objects.filter(descripcion__exact="xbox")
    id_code = Licenses.objects.filter(descripcion__icontains="codigo")
    id_pc = Consoles.objects.filter(descripcion__exact="Pc")
    is_new_account = False
    # try:
    sheet = sheetPs
    m_row = sheet.max_row
    for i in range(2, m_row + 1):
        account = sheet.cell(row=i, column=1).value
        password = sheet.cell(row=i, column=2).value
        id_product = sheet.cell(row=i, column=3).value
        duration_days = 0 if sheet.cell(row=i, column=8).value is None else sheet.cell(row=i, column=8).value
        month_duration = int(duration_days / 30) if duration_days >= 30 else duration_days

        product_for_create = Products.objects.filter(id_product=id_product)

        if account is None or id_product is None:
            continue

        if not product_for_create.exists():
            raise forms.ValidationError(u"el producto para xbox con id " + str(id_product) + " no existe")

        exist_account = ProductAccounts.objects.filter(cuenta=account.lower(),
                                                       producto=int(id_product)).exists()

        sheet_price_xbox_1 = str(sheet.cell(row=i, column=4).value).strip()
        sheet_price_xbox_2 = str(sheet.cell(row=i, column=5).value).strip()
        sheet_price_pc = str(sheet.cell(row=i, column=6).value).strip()
        sheet_price_code = str(sheet.cell(row=i, column=7).value).strip()

        type_account = 1 if sheet_price_code is None else sheet_price_code
        type_account_selected = TypeAccounts.objects.filter(pk=type_account)

        if not exist_account:
            ProductAccounts(
                cuenta=account.lower(),
                password=password,
                activa=True,
                producto=product_for_create.first(),
                tipo_cuenta=type_account_selected.first(),
                dias_duracion=duration_days
            ).save()
            is_new_account = True

        if product_for_create.values().first().get("type_id_id") == 2:
            if sheet_price_xbox_1 != 'None':
                price = sheet_price_xbox_1
                product_name = TypeSuscriptionAccounts.objects.filter(pk=3).first()
                save_price_suscription(product_for_create.first(), product_name, month_duration, duration_days, price)
            if sheet_price_xbox_2 != 'None':
                price = sheet_price_xbox_2
                product_name = TypeSuscriptionAccounts.objects.filter(pk=3).first()
                save_price_suscription(product_for_create.first(), product_name, month_duration, duration_days, price)

            if sheet_price_pc != 'None':
                price = sheet_price_pc
                product_name = TypeSuscriptionAccounts.objects.filter(pk=1).first()
                save_price_suscription(product_for_create.first(), product_name, month_duration, duration_days, price)

            if sheet_price_code != 'None':
                price = sheet_price_code
                product_name = TypeSuscriptionAccounts.objects.filter(pk=2).first()
                save_price_suscription(product_for_create.first(), product_name, month_duration, duration_days, price)

        if check_sheet_price(sheet_price_xbox_1):
            save_or_update_game_detail(id_product, id_xbox, id_primaria, sheet_price_xbox_1, is_new_account, duration_days)
        if check_sheet_price(sheet_price_xbox_2):
            save_or_update_game_detail(id_product, id_xbox, id_secundaria, sheet_price_xbox_2, is_new_account, duration_days)
        if check_sheet_price(sheet_price_pc):
            save_or_update_game_detail(id_product, id_pc, id_primaria, sheet_price_pc, is_new_account, duration_days)
        if check_sheet_price(sheet_price_code):
            save_or_update_game_detail(id_product, id_xbox, id_code, sheet_price_code, is_new_account, duration_days)


class ManegePricesFile:
    def __init__(self):
        path_file_upload = glob.glob(settings.STATIC_URL_FILES + "/*.xlsx")[0]
        path = os.path.abspath(path_file_upload.replace('\\', '/'))
        excel_document = openpyxl.load_workbook(path)
        sheet_ps = excel_document.get_sheet_by_name('cuentas_ps')
        sheet_xbox = excel_document.get_sheet_by_name('cuentas_xbox')
        id_primaria = Licenses.objects.filter(descripcion__icontains="primaria")
        id_secundaria = Licenses.objects.filter(descripcion__icontains="secundaria")
        read_file_ps(sheet_ps, id_primaria, id_secundaria)
        read_file_xbx(sheet_xbox, id_primaria, id_secundaria)


def save_or_update_game_detail(id_product, id_console, id_license, sheet_price, is_new_account, duration_days):
    row_game_detail = GameDetail.objects.filter(producto=id_product,
                                                licencia__exact=id_license[0].id_license,
                                                consola__exact=id_console[0].id_console,
                                                duracion_dias_alquiler=duration_days
                                                )

    #breakpoint()
    product_selected = Products.objects.filter(id_product=id_product)
    if not row_game_detail.exists():
        GameDetail(
            producto=product_selected.first(),
            consola=id_console.first(),
            licencia=id_license.first(),
            stock=1,
            precio=sheet_price,
            estado=True,
            duracion_dias_alquiler=duration_days
        ).save()
        product_selected.update(stock=product_selected.values().get()['stock'] + 1)

    elif product_selected.exists():
        product_selected.update(stock=product_selected.values().get()['stock'] + 1)
        row_game_detail.update(stock=row_game_detail.values().get()['stock'] + 1)
    elif row_game_detail.exists():
        if sheet_price == "x":
            sheet_price = row_game_detail.values().get()['precio']
        row_game_detail.update(precio=sheet_price)

    UpdateStock(product_selected)

def save_price_suscription(product_for_create, product_name, month_duration, duration_days, price):
    product_subscription, created = PriceForSuscription.objects.get_or_create(
        producto=product_for_create,
        tipo_producto=product_name,
        tiempo_alquiler=str(month_duration) + " mes" if month_duration == 1 else str(month_duration) + " meses",
        duracion_dias_alquiler=duration_days,
        precio=price,
        estado=True if duration_days > 0 else False
    )
    # breakpoint()
    product_subscription.stock = F('stock') + 1
    # if not created:
    #     product_subscription.stock = F('stock') + 1
    # else:
    #     product_subscription.stock = 1

    product_subscription.save()
    #if not row_price_suscription.exists():
    #    row_price_suscription.get_or_create()
    #else:
    #    row_price_suscription.update(price=price)


def check_sheet_price(sheet):
    return sheet.strip() != "None" or "x" in sheet