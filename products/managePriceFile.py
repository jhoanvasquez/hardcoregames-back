import os

import openpyxl
from django.conf import settings

from products.models import ProductAccounts, Consoles, Licenses, Products, GameDetail


def readFilePs(sheetPs, id_primaria, id_secundaria):
    id_ps4 = Consoles.objects.filter(descripcion__icontains="playstation 4")
    id_ps5 = Consoles.objects.filter(descripcion__icontains="playstation 5")

    try:
        sheet = sheetPs
        m_row = sheet.max_row

        for i in range(2, m_row + 1):
            account = sheet.cell(row=i, column=1).value
            password = sheet.cell(row=i, column=2).value
            id_product = sheet.cell(row=i, column=3).value

            if account is None or id_product is None:
                continue

            exist_account = ProductAccounts.objects.filter(cuenta=account.lower(),
                                                           producto=int(id_product)).exists()
            if not exist_account:
                ProductAccounts(
                    cuenta=account.lower(),
                    password=password,
                    activa=True,
                    producto=Products.objects.filter(id_product=id_product).first()
                ).save()

            sheet_price_ps4_1 = sheet.cell(row=i, column=4).value
            sheet_price_ps4_2 = sheet.cell(row=i, column=5).value
            sheet_price_ps5_1 = sheet.cell(row=i, column=6).value
            sheet_price_ps5_2 = sheet.cell(row=i, column=7).value

            if sheet_price_ps4_1 is not None:
                saveOrUpdateGameDetail(id_product, id_ps4, id_primaria, sheet_price_ps4_1)
            if sheet_price_ps4_2 is not None:
                saveOrUpdateGameDetail(id_product, id_ps4, id_secundaria, sheet_price_ps4_2)
            if sheet_price_ps5_1 is not None:
                saveOrUpdateGameDetail(id_product, id_ps5, id_primaria, sheet_price_ps5_1)
            if sheet_price_ps5_2 is not None:
                saveOrUpdateGameDetail(id_product, id_ps5, id_secundaria, sheet_price_ps5_2)

    except Exception as e:
        print("problemas en el manejo del archivo cuentas play station" + e)


def readFileXbx(sheetPs, id_primaria, id_secundaria):
    id_xboxs = Consoles.objects.filter(descripcion__icontains="xbox series")
    id_xbox1 = Consoles.objects.filter(descripcion__icontains="xbox one")

    try:
        sheet = sheetPs
        m_row = sheet.max_row

        for i in range(2, m_row + 1):
            account = sheet.cell(row=i, column=1).value
            password = sheet.cell(row=i, column=2).value
            id_product = sheet.cell(row=i, column=3).value

            if account is None or id_product is None:
                continue

            exist_account = ProductAccounts.objects.filter(cuenta=account.lower(),
                                                           producto=int(id_product)).exists()
            if not exist_account:
                ProductAccounts(
                    cuenta=account.lower(),
                    password=password,
                    activa=True,
                    producto=Products.objects.filter(id_product=id_product).first()
                ).save()

            sheet_price_xbox_1 = sheet.cell(row=i, column=4).value
            sheet_price_xbox_2 = sheet.cell(row=i, column=5).value

            if sheet_price_xbox_1 is not None:
                saveOrUpdateGameDetail(id_product, id_xboxs, id_primaria, sheet_price_xbox_1)
                saveOrUpdateGameDetail(id_product, id_xbox1, id_primaria, sheet_price_xbox_1)
            if sheet_price_xbox_2 is not None:
                saveOrUpdateGameDetail(id_product, id_xboxs, id_secundaria, sheet_price_xbox_2)
                saveOrUpdateGameDetail(id_product, id_xbox1, id_secundaria, sheet_price_xbox_2)

    except Exception as e:
        print("problemas en el manejo del archivo cuentas xbox" + e)


class ManegePricesFile:
    def __init__(self):
        path = os.path.abspath(settings.STATIC_URL_FILES+"preciosHardcore.xlsx")
        excel_document = openpyxl.load_workbook(path)
        sheet_ps = excel_document.get_sheet_by_name('cuentas_ps')
        sheet_xbox = excel_document.get_sheet_by_name('cuentas_xbox')
        id_primaria = Licenses.objects.filter(descripcion__icontains="primaria")
        id_secundaria = Licenses.objects.filter(descripcion__icontains="secundaria")
        readFilePs(sheet_ps, id_primaria, id_secundaria)
        readFileXbx(sheet_xbox, id_primaria, id_secundaria)


def saveOrUpdateGameDetail(id_product, id_console, id_license, sheet_price):
    row_game_detail = GameDetail.objects.filter(producto=id_product,
                                                licencia__exact=id_license[0].id_license,
                                                consola__exact=id_console[0].id_console
                                                )

    if not row_game_detail.exists():
        GameDetail(
            producto=Products.objects.filter(id_product=id_product).first(),
            consola=id_console.first(),
            licencia=id_license.first(),
            stock=1,
            precio=sheet_price,
            estado=True
        ).save()
    else:
        row_game_detail.update(precio=sheet_price)
