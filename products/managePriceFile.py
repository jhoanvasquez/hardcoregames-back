import os

import openpyxl


def readFile():
    path = os.path.abspath("files/preciosHardcore.xlsx")
    excel_document = openpyxl.load_workbook(path)
    sheet = excel_document.get_sheet_by_name('cuentas_ps')
    # multiple_cells = sheet['A1':'B3']
    m_row = sheet.max_row
    print(m_row, "m_row")
    for i in range(2, m_row + 1):
        account = sheet.cell(row=i, column=1)
        id_product = sheet.cell(row=i, column=3)
        print(account.value, id_product.value)
    # try:
    #
    # except:
    #     print("archivo no encontrado")


class ManegePricesFile:
    def __init__(self):
        readFile()
