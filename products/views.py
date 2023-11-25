import json
from datetime import date, timedelta

from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from ecommerceHardcoregamesBack import settings
from products.managePriceFile import ManegePricesFile
from products.models import Products, ShoppingCar, Licenses, Consoles, \
    TypeGames, GameDetail, ProductAccounts, SaleDetail, DaysForRentail
from products.productSerializers import ProductsSerializer, ProductSerializer, ShoppingCarSerializer, \
    SerializerForTypes, SerializerGameDetail, SerializerForConsole, SerializerSales, SerializerLicencesName, \
    SerializerDaysForRentail
from utils.SendEmail import SendEmail
from utils.getJsonFromRequest import GetJsonFromRequest


def get_all_products(request):
    if request.method == "GET":
        all_products = Products.objects.filter(stock__gt=0)
        serializer = ProductsSerializer(all_products, many=True)
        payload = {'message': 'proceso exitoso', 'data': serializer.data, 'code': '00', 'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")


def get_favorite_products(request):
    if request.method == "GET":
        all_products = Products.objects.filter(stock__gt=0).order_by('-calification')
        serializer = ProductsSerializer(all_products, many=True)
        payload = {'message': 'proceso exitoso', 'data': serializer.data, 'code': '00', 'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")


def get_news_for_products(request):
    if request.method == "GET":
        all_products = Products.objects.filter(stock__gt=0).order_by('-date_last_modified')
        serializer = ProductsSerializer(all_products, many=True)
        payload = {'message': 'proceso exitoso', 'data': serializer.data, 'code': '00', 'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")


def get_products_by_id(request, id_product):
    if request.method == "GET":
        product = Products.objects.filter(pk=id_product, stock__gt=0)
        if product.exists():
            serializer = ProductSerializer(product, many=True)
            payload = {'message': 'proceso exitoso', 'data': serializer.data[0], 'code': '00', 'status': 200}
            return HttpResponse(JsonResponse(payload), content_type="application/json")
        payload = {'message': 'producto no existente', 'data': {}, 'code': '00', 'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")


def get_products_by_type_console(request, id_console):
    if request.method == "GET":
        console = Consoles.objects.filter(pk=id_console)
        product = Products.objects.filter(consola__in=console, stock__gt=0).exclude(consola__isnull=True)
        if product.exists():
            serializer = ProductSerializer(product, many=True)
            payload = {'message': 'proceso exitoso', 'data': serializer.data, 'code': '00', 'status': 200}
            return HttpResponse(JsonResponse(payload), content_type="application/json")
        payload = {'message': 'producto no existente', 'data': {}, 'code': '00', 'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")


def get_products_by_type_game(request, id_type_game):
    if request.method == "GET":
        product = Products.objects.filter(tipo_juego=id_type_game, stock__gt=0)
        if product.exists():
            serializer = ProductSerializer(product, many=True)
            payload = {'message': 'proceso exitoso', 'data': serializer.data, 'code': '00', 'status': 200}
            return HttpResponse(JsonResponse(payload), content_type="application/json")
        payload = {'message': 'producto no existente', 'data': {}, 'code': '00', 'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")


def get_licences(request):
    if request.method == "GET":
        all_licenses = Licenses.objects.all()
        serializer = SerializerForTypes(all_licenses, many=True)
        payload = {'message': 'proceso exitoso', 'data': serializer.data, 'code': '00', 'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")


def get_consoles(request):
    if request.method == "GET":
        all_consoles = Consoles.objects.all()
        serializer = SerializerForConsole(all_consoles, many=True)
        payload = {'message': 'proceso exitoso', 'data': serializer.data, 'code': '00', 'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")


def get_type_games(request):
    if request.method == "GET":
        all_type_games = TypeGames.objects.all()
        serializer = SerializerForTypes(all_type_games, many=True)
        payload = {'message': 'proceso exitoso', 'data': serializer.data, 'code': '00', 'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")


def get_combination_price_by_game(request, id_product):
    if request.method == "GET":
        xbox_id = Consoles.objects.filter(estado=False)
        combination = GameDetail.objects.filter(producto=id_product, estado=True, )
        if combination.exists():
            if combination.first().consola == xbox_id.first():
                data_response = json.dumps(response_xbox_price(combination))
                payload = {'message': 'proceso exitoso', 'product_id': id_product,
                           'data': json.loads(data_response),
                           'code': '00',
                           'status': 200}
                return HttpResponse(JsonResponse(payload), content_type="application/json")
            serializer = SerializerGameDetail(combination, many=True)
            payload = {'message': 'proceso exitoso', 'product_id': id_product, 'data': serializer.data, 'code': '00',
                       'status': 200}
            return HttpResponse(JsonResponse(payload), content_type="application/json")
        payload = {'message': 'proceso exitoso', 'data': {}, 'code': '00',
                   'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")


def licence_by_product(request, id_product, id_console):
    if request.method == "GET":
        combination = GameDetail.objects.filter(producto=id_product, consola=id_console, stock__gt=0).order_by('-pk')
        serializer = SerializerLicencesName(combination, many=True)
        payload = {'message': 'proceso exitoso', 'product_id': id_product, 'data': serializer.data, 'code': '00',
                   'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")


@csrf_exempt
def shopping_car(request, self=None):
    if request.method == "POST":
        body = GetJsonFromRequest.__int__(self, request)
        user_id = body['user_id']
        combination_id = body['id_combination']
        state = body['state']
        user = User.objects.filter(pk=user_id)
        product = GameDetail.objects.filter(pk=combination_id)
        if product.count() > 0 and user.count() > 0:
            shopping_car = ShoppingCar(
                usuario=user.get(),
                producto=product.get(),
                estado=state
            )
            shopping_car.save()
            payload = {'message': 'proceso exitoso', 'data': True, 'code': '00', 'status': 200}
            return HttpResponse(JsonResponse(payload), content_type="application/json")
        payload = {'message': 'producto no existente o usuario no existente', 'data': {}, 'code': '00', 'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")


def get_shopping_car(request):
    if request.method == "GET":
        user_id = request.GET['user_id']
        user = ShoppingCar.objects.filter(usuario=user_id, producto__stock__gt=0)
        if user.exists():
            if request.GET['state']:
                state = True if request.GET['state'] == "true" else False
                shopping_cars = ShoppingCar.objects.filter(usuario=user_id, estado=state,
                                                           producto__stock__gt=0).order_by('pk')
            else:
                shopping_cars = ShoppingCar.objects.filter(usuario=user_id, producto__stock__gt=0).order_by('pk')
            shopping_cars_serialized = ShoppingCarSerializer(shopping_cars, many=True)
            payload = {'message': 'proceso exitoso', 'user_id': int(user_id),
                       'data': shopping_cars_serialized.data, 'code': '00', 'status': 200}
            return HttpResponse(JsonResponse(payload), content_type="application/json")
        payload = {'message': 'producto no existente o usuario no existente', 'data': {}, 'code': '00', 'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")


def salesByUser(request, id_user):
    if request.method == "GET":
        sales_by_user = SaleDetail.objects.filter(usuario=id_user).order_by('-pk')
        serializer = SerializerSales(sales_by_user, many=True)
        payload = {'message': 'proceso exitoso', 'data': serializer.data, 'code': '00', 'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")


def daysForRentail(request):
    if request.method == "GET":
        days_rentail = DaysForRentail.objects.all()
        serializer = SerializerDaysForRentail(days_rentail, many=True)
        payload = {'message': 'proceso exitoso', 'data': serializer.data, 'code': '00', 'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")


@csrf_exempt
def confirmSale(request):
    if request.method == "POST":
        json_request = json.loads(request.body)
        id_user = json_request['id_user']
        message_html = "";

        for item in json_request['data']:
            id_combination = item['id_combination']
            combination = GameDetail.objects.filter(pk=id_combination, stock__gt=0)
            if combination.exists():
                product_id = combination.first().producto.id_product
                product_selected = Products.objects.filter(id_product=product_id)
                account_selected = ProductAccounts.objects.filter(producto_id=product_id, activa=True)

                new_stock = product_selected.values().get()["stock"] - 1
                if new_stock > 0:
                    combination.update(stock=combination.values().get()['stock'] - 1)
                    product_selected.update(stock=new_stock)

                if product_selected.values().get()['stock'] == 0:
                    account_selected.first().update(activa=False)
                create_sale(item, id_user, account_selected)
                deleteShoppingProduct(id_combination, id_user)
                message_html += buildDivHtml(product_selected, combination, account_selected)

        if settings.SEND_EMAIL == "true":
            sendEmailNotification(id_user, message_html)
        payload = {'message': 'proceso exitoso',
                   'response': True, 'code': '00', 'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")
    payload = {'message': 'no se encuentran productos existentes', 'data': {}, 'code': '00', 'status': 200}
    return HttpResponse(JsonResponse(payload), content_type="application/json")


@csrf_exempt
def update_shopping_car(request, shooping_car_id, self=None):
    if request.method == "PUT":
        body = GetJsonFromRequest.__int__(self, request)
        state = body['state']
        shooping_car = ShoppingCar.objects.filter(pk=shooping_car_id)
        if shooping_car.count() > 0:
            ShoppingCar.objects.filter(pk=shooping_car_id).update(
                estado=state
            )
            payload = {'message': 'proceso exitoso', 'code': '00', 'status': 200}
            return HttpResponse(JsonResponse(payload), content_type="application/json")
        payload = {'message': 'producto no existente o usuario no existente', 'data': {}, 'code': '00', 'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")


@csrf_exempt
def delete_product_shopping_car(request, shooping_car_id):
    if request.method == "DELETE":
        shooping_car = ShoppingCar.objects.filter(pk=shooping_car_id)
        if shooping_car.count() > 0:
            ShoppingCar.objects.filter(pk=shooping_car_id).delete()
            payload = {'message': 'proceso exitoso', 'code': '00', 'status': 200}
            return HttpResponse(JsonResponse(payload), content_type="application/json")
        payload = {'message': 'producto no existente', 'data': {}, 'code': '00', 'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")


def sendEmail(request):
    SendEmail().__int__()
    return HttpResponse(JsonResponse({'message': 'Email enviado', "status": 200, "code": "00"}),
                        content_type="application/json")


def manageFile(request):
    ManegePricesFile()
    return HttpResponse(JsonResponse({'message': 'File procesado', "status": 200, "code": "00"}),
                        content_type="application/json")


def response_xbox_price(queryset):
    data = []
    for item in queryset:
        data.append({
            'pk': item.id_game_detail,
            'consola': item.consola.get_id_console(),
            'desc_console': "Xbox one",
            'licencia': item.licencia.get_id_licence(),
            'desc_licence': item.licencia.__str__(),
            'stock': 1,
            'precio': item.precio
        })
        data.append({
            'pk': item.id_game_detail,
            'consola': item.consola.get_id_console(),
            'desc_console': "Xbox Series",
            'licencia': item.licencia.get_id_licence(),
            'desc_licence': item.licencia.__str__(),
            'stock': 1,
            'precio': item.precio
        })
    return data


def create_sale(sale, id_user, account):
    user = User.objects.filter(pk=id_user).first()
    combination = GameDetail.objects.filter(pk=sale['id_combination']).first()
    today = date.today()
    date_expiration = None
    if sale['is_rentail']:
        date_expiration = today + timedelta(days=int(sale['days_rentail']))
    sale_detail = SaleDetail(
        usuario=user,
        producto=combination.producto,
        cuenta=account.first(),
        fecha_vencimiento=date_expiration

    )
    sale_detail.save()


def deleteShoppingProduct(id_comination: str, id_user: str):
    ShoppingCar.objects.filter(usuario=id_user, producto__exact=id_comination).delete()


def sendEmailNotification(user_id, message_html):
    email_to = User.objects.filter(pk=user_id).first().email
    soup = BeautifulSoup(settings.EMAIL_FOR_SALE, features="html.parser")
    extra_soup = BeautifulSoup(message_html, 'html.parser')
    body = soup.find("div", {"id": "body"})
    body.append(extra_soup)
    SendEmail().__int__(str(soup), settings.SUBJECT_EMAIL_FOR_SALE, email_to)


def buildDivHtml(product, combination, account):
    string_pass = account.first().password
    if string_pass is None:
        string_pass = ""
    return f'''<div style="margin-bottom: 20%;">
               <h3>{product.first().title}</h3>
               <div style="margin-bottom: auto;">
                  <div style="float:right;font-weight:600;font-size:16px;">
                     <img src="{product.first().image}" width="30" class="CToWUd" data-bit="iit">
                  </div>
                  <li style="margin-bottom: 10px;">
                     <lu>
                        <b>Usuario:</b><br> {account.first().cuenta}
                     </lu>
                  </li>
                  <li>
                     <lu>
                        <b>Contraseña:</b> {string_pass}
                     </lu>
                  </li> 
                  <li>
                     <lu>
                        <b>Licencia:</b> {combination.first().licencia}
                     </lu>
                  </li>
                  <li>
                     <lu>
                        <b>Consola:</b> {combination.first().consola}
                     </lu>
                  </li>
               </div>
            </div>
            <hr style="border-color:#e0e0e0;border-width:1px">'''
