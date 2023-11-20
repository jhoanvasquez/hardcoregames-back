import os

import openpyxl
from django import forms
from django.conf import settings

from products.models import ProductAccounts, Consoles, Licenses, Products, GameDetail


def readFilePs(sheetPs, id_primaria, id_secundaria):
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

        if not product_for_create.exists():
            raise forms.ValidationError(u"el producto para play station con id " + str(id_product) + " no existe")

        if account is None or id_product is None:
            continue

        exist_account = ProductAccounts.objects.filter(cuenta=account.lower(),
                                                       producto=int(id_product)).exists()

        if not exist_account:
            ProductAccounts(
                cuenta=account.lower(),
                password=password,
                activa=True,
                producto=product_for_create.first()
            ).save()
            is_new_account = True
        sheet_price_ps4_1 = sheet.cell(row=i, column=4).value
        sheet_price_ps4_2 = sheet.cell(row=i, column=5).value
        sheet_price_ps5_1 = sheet.cell(row=i, column=6).value
        sheet_price_ps5_2 = sheet.cell(row=i, column=7).value

        if sheet_price_ps4_1 is not None:
            saveOrUpdateGameDetail(id_product, id_ps4, id_primaria, sheet_price_ps4_1, is_new_account)
        if sheet_price_ps4_2 is not None:
            saveOrUpdateGameDetail(id_product, id_ps4, id_secundaria, sheet_price_ps4_2, is_new_account)
        if sheet_price_ps5_1 is not None:
            saveOrUpdateGameDetail(id_product, id_ps5, id_primaria, sheet_price_ps5_1, is_new_account)
        if sheet_price_ps5_2 is not None:
            saveOrUpdateGameDetail(id_product, id_ps5, id_secundaria, sheet_price_ps5_2, is_new_account)

    # except Exception as e:
    #     print("problemas en el manejo del archivo cuentas play station " + str(e))


def readFileXbx(sheetPs, id_primaria, id_secundaria):
    id_xbox = Consoles.objects.filter(descripcion__exact="xbox")
    is_new_account = False
    try:
        sheet = sheetPs
        m_row = sheet.max_row

        for i in range(2, m_row + 1):
            account = sheet.cell(row=i, column=1).value
            password = sheet.cell(row=i, column=2).value
            id_product = sheet.cell(row=i, column=3).value

            product_for_create = Products.objects.filter(id_product=id_product)

            if not product_for_create.exists():
                raise forms.ValidationError(u"el producto para play station con id " + str(id_product) + " no existe")

            if account is None or id_product is None:
                continue

            exist_account = ProductAccounts.objects.filter(cuenta=account.lower(),
                                                           producto=int(id_product)).exists()

            if not exist_account:
                ProductAccounts(
                    cuenta=account.lower(),
                    password=password,
                    activa=True,
                    producto=product_for_create.first()
                ).save()
                is_new_account = True

            sheet_price_xbox_1 = sheet.cell(row=i, column=4).value
            sheet_price_xbox_2 = sheet.cell(row=i, column=5).value

            if sheet_price_xbox_1 is not None:
                saveOrUpdateGameDetail(id_product, id_xbox, id_primaria, sheet_price_xbox_1, is_new_account)
            if sheet_price_xbox_2 is not None:
                saveOrUpdateGameDetail(id_product, id_xbox, id_secundaria, sheet_price_xbox_2, is_new_account)

    except Exception as e:
        print("problemas en el manejo del archivo cuentas xbox " + str(e))


class ManegePricesFile:
    def __init__(self):
        path = os.path.abspath(settings.STATIC_URL_FILES + "preciosHardcore.xlsx")
        excel_document = openpyxl.load_workbook(path)
        sheet_ps = excel_document.get_sheet_by_name('cuentas_ps')
        sheet_xbox = excel_document.get_sheet_by_name('cuentas_xbox')
        id_primaria = Licenses.objects.filter(descripcion__icontains="primaria")
        id_secundaria = Licenses.objects.filter(descripcion__icontains="secundaria")
        readFilePs(sheet_ps, id_primaria, id_secundaria)
        readFileXbx(sheet_xbox, id_primaria, id_secundaria)


def saveOrUpdateGameDetail(id_product, id_console, id_license, sheet_price, is_new_account):
    row_game_detail = GameDetail.objects.filter(producto=id_product,
                                                licencia__exact=id_license[0].id_license,
                                                consola__exact=id_console[0].id_console
                                                )

    product_selected = Products.objects.filter(id_product=id_product)
    if not row_game_detail.exists():
        GameDetail(
            producto=product_selected.first(),
            consola=id_console.first(),
            licencia=id_license.first(),
            stock=1,
            precio=sheet_price,
            estado=True
        ).save()
        product_selected.update(stock = product_selected.values().get()['stock'] + 1)

    elif is_new_account:
        # row_game_detail.update(stock = row_game_detail.values().get()['stock'] + 1)
        product_selected.update(stock = product_selected.values().get()['stock'] + 1)
    else:
        row_game_detail.update(precio=sheet_price)
