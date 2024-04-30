import json
from datetime import date, timedelta

from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import F, Sum
from django.http import HttpResponse, JsonResponse
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt

from ecommerceHardcoregamesBack import settings
from products.managePriceFile import ManegePricesFile
from products.models import Products, ShoppingCar, Licenses, Consoles, \
    TypeGames, GameDetail, ProductAccounts, SaleDetail, DaysForRentail, PriceForSuscription, TypeAccounts, \
    VariablesSistema, TypeSuscriptionAccounts
from products.productSerializers import ProductsSerializer, ProductSerializer, ShoppingCarSerializer, \
    SerializerForTypes, SerializerGameDetail, SerializerForConsole, SerializerSales, SerializerLicencesName, \
    SerializerDaysForRentail, SerializerPriceSuscriptionProduct, SerializerForVariables
from users.models import User_Customized
from utils.SendEmail import SendEmail
from utils.getJsonFromRequest import GetJsonFromRequest


def get_all_products(request):
    if request.method == "GET":
        size = request.GET.get('size')
        page = request.GET.get('page')
        cache_key = f"all_products_{size}_{page}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return JsonResponse(cached_data)

        all_products = Products.objects.filter(stock__gt=0)
        count_rows = all_products.count()
        if size == "all":
            paginator = Paginator(all_products, 1 if count_rows == 0 else count_rows)
        else:
            paginator = Paginator(all_products, size)
        try:
            response = paginator.page(page)
        except PageNotAnInteger:
            response = paginator.page(1)
        except EmptyPage:
            response = paginator.page(paginator.num_pages)

        serializer = ProductSerializer(response, many=True)
        for i in serializer.data:
            stock = GameDetail.objects.filter(producto=i['pk'],
                                              stock__gt=0).aggregate(Sum('stock'))['stock__sum']
            i['stock'] = 0 if stock is None else stock
        payload = {'message': 'proceso exitoso', 'data': serializer.data, 'total_items': count_rows,
                   'code': '00', 'status': 200}
        # Cache the result
        cache.set(cache_key, payload)
        return HttpResponse(JsonResponse(payload), content_type="application/json")


def get_favorite_products(request):
    if request.method == "GET":
        size = request.GET.get('size')
        page = request.GET.get('page')
        # Check if the result is already cached
        cache_key = f"favorite_products_{size}_{page}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return JsonResponse(cached_data)
        all_products = Products.objects.filter(stock__gt=0).order_by('-calification')
        # [10:20]

        count_rows = all_products.count()
        if size == "all":
            paginator = Paginator(all_products, 1 if count_rows == 0 else count_rows)
        else:
            paginator = Paginator(all_products, size)
        try:
            response = paginator.page(page)
        except PageNotAnInteger:
            response = paginator.page(1)
        except EmptyPage:
            response = paginator.page(paginator.num_pages)

        serializer = ProductSerializer(response, many=True)
        for i in serializer.data:
            stock = GameDetail.objects.filter(producto=i['pk'],
                                              stock__gt=0).aggregate(Sum('stock'))['stock__sum']
            i['stock'] = 0 if stock is None else stock
        payload = {
            'message': 'Proceso exitoso',
            'data': serializer.data,
            'total_items': count_rows,
            'code': '00',
            'status': 200
        }

        # Cache the result
        cache.set(cache_key, payload)

        return JsonResponse(payload)


def get_featured_products(request):
    if request.method == "GET":
        size = request.GET.get('size')
        page = request.GET.get('page')
        cache_key = f"featured_products_{size}_{page}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return JsonResponse(cached_data)
        all_products = Products.objects.filter(stock__gt=0, destacado=True).order_by('-pk')
        count_rows = all_products.count()
        if size == "all":
            paginator = Paginator(all_products, 1 if count_rows == 0 else count_rows)
        else:
            paginator = Paginator(all_products, size)
        try:
            response = paginator.page(page)
        except PageNotAnInteger:
            response = paginator.page(1)
        except EmptyPage:
            response = paginator.page(paginator.num_pages)

        serializer = ProductSerializer(response, many=True)
        for i in serializer.data:
            stock = GameDetail.objects.filter(producto=i['pk'],
                                              stock__gt=0).aggregate(Sum('stock'))['stock__sum']
            i['stock'] = 0 if stock is None else stock
        payload = {'message': 'proceso exitoso', 'data': serializer.data, 'total_items': count_rows,
                   'code': '00', 'status': 200}
        # Cache the result
        cache.set(cache_key, payload)
        return HttpResponse(JsonResponse(payload), content_type="application/json")


def get_news_for_products(request):
    if request.method == "GET":
        size = request.GET.get('size')
        page = request.GET.get('page')
        cache_key = f"news_products_{size}_{page}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return JsonResponse(cached_data)

        all_products = Products.objects.filter(stock__gt=0).order_by('-date_last_modified')
        count_rows = all_products.count()
        if size == "all":
            paginator = Paginator(all_products, 1 if count_rows == 0 else count_rows)
        else:
            paginator = Paginator(all_products, size)
        try:
            response = paginator.page(page)
        except PageNotAnInteger:
            response = paginator.page(1)
        except EmptyPage:
            response = paginator.page(paginator.num_pages)

        serializer = ProductSerializer(response, many=True)
        for i in serializer.data:
            stock = GameDetail.objects.filter(producto=i['pk'],
                                              stock__gt=0).aggregate(Sum('stock'))['stock__sum']
            i['stock'] = 0 if stock is None else stock
        payload = {'message': 'proceso exitoso', 'data': serializer.data, 'total_items': count_rows,
                   'code': '00', 'status': 200}
        # Cache the result
        cache.set(cache_key, payload)
        return HttpResponse(JsonResponse(payload), content_type="application/json")


def get_products_by_id(request, id_product):
    if request.method == "GET":
        product = Products.objects.filter(pk=id_product, stock__gt=0)
        if product.exists():
            serializer = ProductSerializer(product, many=True)
            serializer.data[0]['stock'] = GameDetail.objects.filter(producto=id_product,
                                                                    stock__gt=0).aggregate(Sum('stock'))['stock__sum']
            payload = {'message': 'proceso exitoso', 'data': serializer.data[0], 'code': '00', 'status': 200}
            return HttpResponse(JsonResponse(payload), content_type="application/json")
        payload = {'message': 'producto no existente', 'data': {}, 'code': '00', 'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")

def find_product_by_name(request, name_product):
    if request.method == "GET":
        if name_product != "null":
            product = (Products.objects.filter(title__icontains=name_product,
                                              stock__gt=0)|
                       Products.objects.filter(title__icontains=name_product.replace(" ", ""),
                                               stock__gt=0)
                       )

            if product.exists():
                serializer = ProductSerializer(product, many=True)
                payload = {'message': 'proceso exitoso', 'data': serializer.data, 'code': '00', 'status': 200}
                return HttpResponse(JsonResponse(payload), content_type="application/json")
        payload = {'message': 'producto no existente', 'data': [], 'code': '00', 'status': 200}
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


@csrf_exempt
def filter_product(request, ):
    if request.method == "POST":
        json_request = json.loads(request.body)
        id_console = json_request['id_console']
        id_category = json_request['id_category']
        range_min = json_request['range_min']
        range_max = json_request['range_max']
        size = json_request['size']
        page = json_request['page']

        if id_console is not None and id_category is None and range_min is None and range_max is None:
            cache_key = f"filter_console_{size}_{page}_{id_console}"
            cached_data = cache.get(cache_key)

            if cached_data:
                return JsonResponse(cached_data)

            product = Products.objects.filter(consola=id_console)
            count_rows = product.count()
            if size == "all":
                paginator = Paginator(product, 1 if count_rows == 0 else count_rows)
            else:
                paginator = Paginator(product, size)
            try:
                response = paginator.page(page)
            except PageNotAnInteger:
                response = paginator.page(1)
            except EmptyPage:
                response = paginator.page(paginator.num_pages)

            serializer = ProductSerializer(response, many=True)
            payload = {'message': 'proceso exitoso',
                       'data': serializer.data,
                       'code': '00',
                       'total_items': count_rows,
                       'status': 200}

            cache.set(cache_key, payload, timeout=259200)
            return HttpResponse(JsonResponse(payload), content_type="application/json")

        elif id_console is None and id_category is not None and range_min is None and range_max is None:
            cache_key = f"filter_category_{size}_{page}_{id_category}"
            cached_data = cache.get(cache_key)
            if cached_data:
                return JsonResponse(cached_data)

            product = Products.objects.filter(tipo_juego=id_category)
            count_rows = product.count()
            if size == "all":
                paginator = Paginator(product, 1 if count_rows == 0 else count_rows)
            else:
                paginator = Paginator(product, size)
            try:
                response = paginator.page(page)
            except PageNotAnInteger:
                response = paginator.page(1)
            except EmptyPage:
                response = paginator.page(paginator.num_pages)
            serializer = ProductSerializer(response, many=True)
            payload = {'message': 'proceso exitoso',
                       'data': serializer.data,
                       'total_items': count_rows,
                       'code': '00',
                       'status': 200}
            cache.set(cache_key, payload, timeout=259200)
            return HttpResponse(JsonResponse(payload), content_type="application/json")

        elif (id_console is not None and id_category is not None and range_min is None and
              range_max is None):

            cache_key = f"filter_console_category_{size}_{page}_{id_console}_{id_category}"
            cached_data = cache.get(cache_key)
            if cached_data:
                return JsonResponse(cached_data)

            product = Products.objects.filter(consola=id_console, tipo_juego=id_category)
            count_rows = product.count()
            if size == "all":
                paginator = Paginator(product, 1 if count_rows == 0 else count_rows)
            else:
                paginator = Paginator(product, size)
            try:
                response = paginator.page(page)
            except PageNotAnInteger:
                response = paginator.page(1)
            except EmptyPage:
                response = paginator.page(paginator.num_pages)
            serializer = ProductSerializer(response, many=True)
            payload = {'message': 'proceso exitoso',
                       'data': serializer.data,
                       'code': '00',
                       'total_items': count_rows,
                       'status': 200}
            cache.set(cache_key, payload, timeout=259200)
            return HttpResponse(JsonResponse(payload), content_type="application/json")

        elif (id_console is not None and id_category is not None and range_min is not None and
              range_max is not None):

            cache_key = f"filter_console_category_range_{size}_{page}_{id_console}_{id_category}_{range_min}_{range_max}"
            cached_data = cache.get(cache_key)
            if cached_data:
                return JsonResponse(cached_data)

            product = Products.objects.filter(consola=id_console,
                                              tipo_juego=id_category,
                                              price__gte=range_min,
                                              price__lt=range_max)
            count_rows = product.count()
            if size == "all":
                paginator = Paginator(product, 1 if count_rows == 0 else count_rows)
            else:
                paginator = Paginator(product, size)
            try:
                response = paginator.page(page)
            except PageNotAnInteger:
                response = paginator.page(1)
            except EmptyPage:
                response = paginator.page(paginator.num_pages)
            serializer = ProductSerializer(response, many=True)
            payload = {'message': 'proceso exitoso',
                       'data': serializer.data,
                       'code': '00',
                       'total_items': count_rows,
                       'status': 200}

            cache.set(cache_key, payload, timeout=259200)
            return HttpResponse(JsonResponse(payload), content_type="application/json")

        elif (id_console is not None and id_category is None and range_min is not None and
              range_max is not None):

            cache_key = f"filter_console_range_{size}_{page}_{id_console}_{range_min}_{range_max}"
            cached_data = cache.get(cache_key)
            if cached_data:
                return JsonResponse(cached_data)

            product = Products.objects.filter(consola=id_console,
                                              price__gte=range_min,
                                              price__lt=range_max)
            count_rows = product.count()
            if size == "all":
                paginator = Paginator(product, 1 if count_rows == 0 else count_rows)
            else:
                paginator = Paginator(product, size)
            try:
                response = paginator.page(page)
            except PageNotAnInteger:
                response = paginator.page(1)
            except EmptyPage:
                response = paginator.page(paginator.num_pages)
            serializer = ProductSerializer(response, many=True)
            payload = {'message': 'proceso exitoso',
                       'data': serializer.data,
                       'code': '00',
                       'total_items': count_rows,
                       'status': 200}
            cache.set(cache_key, payload, timeout=259200)
            return HttpResponse(JsonResponse(payload), content_type="application/json")

        elif (id_console is None and id_category is not None and range_min is not None and
              range_max is not None):

            cache_key = f"filter_category_range_{size}_{page}_{id_category}_{range_min}_{range_max}"
            cached_data = cache.get(cache_key)
            if cached_data:
                return JsonResponse(cached_data)

            product = Products.objects.filter(tipo_juego=id_category,
                                              price__gte=range_min,
                                              price__lt=range_max)
            count_rows = product.count()
            if size == "all":
                paginator = Paginator(product, 1 if count_rows == 0 else count_rows)
            else:
                paginator = Paginator(product, size)
            try:
                response = paginator.page(page)
            except PageNotAnInteger:
                response = paginator.page(1)
            except EmptyPage:
                response = paginator.page(paginator.num_pages)
            serializer = ProductSerializer(response, many=True)
            payload = {'message': 'proceso exitoso',
                       'data': serializer.data,
                       'code': '00',
                       'total_items': count_rows,
                       'status': 200}
            cache.set(cache_key, payload, timeout=259200)
            return HttpResponse(JsonResponse(payload), content_type="application/json")

        elif (id_console is None and id_category is None and range_min is not None and
              range_max is not None):

            cache_key = f"filter_range_{size}_{page}_{range_min}_{range_max}"
            cached_data = cache.get(cache_key)
            if cached_data:
                return JsonResponse(cached_data)

            product = Products.objects.filter(price__gte=range_min,
                                              price__lt=range_max)
            count_rows = product.count()
            if size == "all":
                paginator = Paginator(product, count_rows)
            else:
                paginator = Paginator(product, size)
            try:
                response = paginator.page(page)
            except PageNotAnInteger:
                response = paginator.page(1)
            except EmptyPage:
                response = paginator.page(paginator.num_pages)
            serializer = ProductSerializer(response, many=True)
            payload = {'message': 'proceso exitoso',
                       'data': serializer.data,
                       'code': '00',
                       'total_items': count_rows,
                       'status': 200}
            cache.set(cache_key, payload, timeout=259200)
            return HttpResponse(JsonResponse(payload), content_type="application/json")

        payload = {'message': 'producto no existente', 'data': {}, 'code': '00', 'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")


def get_products_by_type_game(request, id_type_game):
    if request.method == "GET":
        cache_key = "products_by_type_game"
        cached_data = cache.get(cache_key)
        if cached_data:
            return JsonResponse(cached_data)

        product = Products.objects.filter(tipo_juego=id_type_game, stock__gt=0)
        if product.exists():
            serializer = ProductSerializer(product, many=True)
            payload = {'message': 'proceso exitoso',
                       'data': serializer.data,
                       'code': '00',
                       'status': 200}
            cache.set(cache_key, payload, timeout=259200)
            return HttpResponse(JsonResponse(payload), content_type="application/json")
        payload = {'message': 'producto no existente', 'data': {}, 'code': '00', 'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")


def get_products_by_range_price(request):
    if request.method == "GET":
        range_min = request.GET['range_min']
        range_max = request.GET['range_max']
        product = Products.objects.filter(price__gt=range_min, price__lte=range_max, stock__gt=0)
        if product.exists():
            serializer = ProductSerializer(product, many=True)
            payload = {'message': 'proceso exitoso', 'data': serializer.data, 'code': '00', 'status': 200}
            return HttpResponse(JsonResponse(payload), content_type="application/json")
        payload = {'message': 'producto no existente', 'data': {}, 'code': '00', 'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")


def price_suscription_product(request, id_product, type_account):
    if request.method == "GET":
        id_type_account_req = TypeSuscriptionAccounts.objects.filter(pk=type_account).first()
        console_name = get_name_console_suscription(type_account)

        license_name = get_name_licencia_suscription(type_account)
        stock_for_product = GameDetail.objects.filter(
            producto=id_product,
            consola=console_name,
            licencia__in=license_name,
            stock__gt=0
        )
        if not stock_for_product.exists():
            payload = {'message': 'producto no existente', 'data': [], 'code': '00', 'status': 200}
            return HttpResponse(JsonResponse(payload), content_type="application/json")

        if "Cuenta" in id_type_account_req.__str__():
            type_account_sale = 1
        else:
            type_account_sale = 2

        product_accounts = ProductAccounts.objects.filter(producto=id_product,
                                                          tipo_cuenta=type_account_sale,
                                                          activa=True)
        duration_account = get_duration_account(product_accounts)

        # if type_product is not None:
        product = PriceForSuscription.objects.filter(producto=id_product,
                                                     estado=True,
                                                     duracion_dias_alquiler__in=duration_account,
                                                     tipo_producto__in=[type_account]
                                                     ).distinct('tiempo_alquiler')
        # else:
        #    product = PriceForSuscription.objects.filter(producto=id_product,
        #                                                 estado=True,
        #                                                 duracion_dias_alquiler__in=duration_account
        #                                                 ).distinct('tiempo_alquiler')

        if product.exists():
            serializer = SerializerPriceSuscriptionProduct(product, many=True)
            payload = {'message': 'proceso exitoso', 'data': serializer.data, 'code': '00', 'status': 200}
            return HttpResponse(JsonResponse(payload), content_type="application/json")
        payload = {'message': 'producto no existente', 'data': [], 'code': '00', 'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")


def get_licences(request):
    if request.method == "GET":
        cache_key = "licences"
        cached_data = cache.get(cache_key)
        if cached_data:
            return JsonResponse(cached_data)

        all_licenses = Licenses.objects.all()
        serializer = SerializerForTypes(all_licenses, many=True)
        payload = {'message': 'proceso exitoso',
                   'data': serializer.data,
                   'code': '00',
                   'status': 200}
        cache.set(cache_key, payload)
        return HttpResponse(JsonResponse(payload), content_type="application/json")


def get_consoles(request):
    if request.method == "GET":
        cache_key = "consoles"
        cached_data = cache.get(cache_key)
        if cached_data:
            return JsonResponse(cached_data)
        all_consoles = Consoles.objects.all()
        serializer = SerializerForConsole(all_consoles, many=True)
        payload = {'message': 'proceso exitoso',
                   'data': serializer.data,
                   'code': '00',
                   'status': 200}
        cache.set(cache_key, payload, timeout=259200)
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
        payload = {'message': 'proceso exitoso', 'data': {}, 'code': '00', 'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")


def licence_by_product(request, id_product, id_console):
    if request.method == "GET":
        combination = GameDetail.objects.filter(producto=id_product, consola=id_console, stock__gt=0).order_by('-pk')
        serializer = SerializerLicencesName(combination, many=True)
        payload = {'message': 'proceso exitoso', 'product_id': id_product, 'data': serializer.data,
                   'code': '00', 'status': 200}
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


def sales_by_user(request, id_user):
    if request.method == "GET":
        sales_by_user = (SaleDetail.objects.filter(usuario=id_user,
                                                   fecha_vencimiento__gt=now()
                                                   ).order_by('-pk') |
                         SaleDetail.objects.filter(usuario=id_user,
                                                   fecha_vencimiento=None
                                                   ).order_by('-pk'))
        serializer = SerializerSales(sales_by_user, many=True)
        payload = {'message': 'proceso exitoso', 'data': serializer.data, 'code': '00', 'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")


def days_for_rentail(request):
    if request.method == "GET":
        days_rentail = DaysForRentail.objects.all()
        serializer = SerializerDaysForRentail(days_rentail, many=True)
        payload = {'message': 'proceso exitoso', 'data': serializer.data, 'code': '00', 'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")


def type_accounts(request):
    if request.method == "GET":
        type_accounts = TypeSuscriptionAccounts.objects.all()
        serializer = SerializerForTypes(type_accounts, many=True)
        payload = {'message': 'proceso exitoso', 'data': serializer.data, 'code': '00', 'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")


def system_variables(request, variable):
    if request.method == "GET":
        system_variables = VariablesSistema.objects.filter(nombre_variable=variable, estado=True)
        serializer = SerializerForVariables(system_variables, many=True)
        payload = {'message': 'proceso exitoso', 'data': serializer.data[0], 'code': '00', 'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")


def system_variables_group(request, variable):
    if request.method == "GET":
        system_variables = VariablesSistema.objects.filter(nombre_variable__icontains=variable, estado=True)
        serializer = SerializerForVariables(system_variables, many=True)
        payload = {'message': 'proceso exitoso', 'data': serializer.data, 'code': '00', 'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")


@csrf_exempt
def confirm_sale(request):
    if request.method == "POST":
        json_request = json.loads(request.body)
        id_user = json_request['id_user']
        message_html = ""

        for item in json_request['data']:
            if item['id_combination'] is None:
                id_product = item['id_product']
                combination_id = search_combination(id_product, item['type_account'])
                combination_selected = GameDetail.objects.filter(pk=combination_id)
            else:
                combination_selected = GameDetail.objects.filter(pk=item['id_combination'], stock__gt=0)

            if Products.objects.filter(pk=item['id_product']).values().first().get("type_id_id") == 1:
                type_account = 1 if item['type_account'] is None else item['type_account']
            else:
                type_account = get_type_account_suscription(item['type_account'])

            days_rentail = 0 if item['days_rentail'] is None else item['days_rentail']

            account_selected = ProductAccounts.objects.filter(producto_id=item['id_product'],
                                                              dias_duracion=days_rentail,
                                                              activa__exact=True,
                                                              tipo_cuenta__exact=type_account
                                                              ).first()

            if combination_selected.exists() and account_selected is not None:
                id_combination = combination_selected.first().id_game_detail
                item['id_combination'] = id_combination
                item['days_rentail'] = days_rentail
                product_selected = Products.objects.filter(id_product=item['id_product'])

                new_stock = product_selected.values().get()["stock"] - 1
                create_sale(item, id_user, account_selected)
                update_points_sale(id_user, product_selected.first().puntos_venta)
                delete_shopping_product(id_combination, id_user)

                message_html += build_div_html(product_selected, combination_selected, account_selected)

                if new_stock >= 0:
                    combination_selected.update(stock=F('stock') - 1)
                    product_selected.update(stock=new_stock)
                if product_selected.values().get()['stock'] == 0:
                    (ProductAccounts.objects.filter(pk=account_selected.id_product_accounts)
                     .update(activa=False))
            else:
                payload = {'message': 'Ha ocurrido un error, intente mas tarde o contactese con el administrador',
                           'response': True, 'code': '00', 'status': 200}
                return HttpResponse(JsonResponse(payload), content_type="application/json")

        if settings.SEND_EMAIL == "true":
            send_email_notification(id_user, message_html)
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
def update_points_by_user(request, user_id, self=None):
    if request.method == "PUT":
        body = GetJsonFromRequest.__int__(self, request)
        points = body['points']
        user_selected = User.objects.filter(pk=user_id)
        if user_selected.count() > 0:
            User_Customized.objects.filter(user=user_id).update(
                puntos=points
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
    # check_products_expired()
    send_email_notification(2, "<html><head>prueba</head><body>prueba</body></html>")
    return HttpResponse(JsonResponse({'message': "prueba email", "status": 200, "code": "00"}),
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
            'stock': item.stock,
            'precio': item.precio
        })
        data.append({
            'pk': item.id_game_detail,
            'consola': item.consola.get_id_console(),
            'desc_console': "Xbox Series",
            'licencia': item.licencia.get_id_licence(),
            'desc_licence': item.licencia.__str__(),
            'stock': item.stock,
            'precio': item.precio
        })
    return data


def create_sale(sale, id_user, account_selected):
    user = User.objects.filter(pk=id_user).first()
    combination = GameDetail.objects.filter(pk=sale['id_combination']).first()
    today = date.today()
    date_expiration = None
    if sale['is_rentail']:
        date_expiration = today + timedelta(days=int(sale['days_rentail']))
    sale_detail = SaleDetail(
        usuario=user,
        producto=combination.producto,
        cuenta=account_selected,
        fecha_vencimiento=date_expiration,
        combinacion=combination
    )
    sale_detail.save()


def update_points_sale(id_user, points):
    instance_user = User.objects.filter(pk=id_user).first()
    User_Customized.objects.filter(user=instance_user).update(
        puntos=F("puntos") + points
    )


def delete_shopping_product(id_combination: str, id_user: str):
    product_shoping_car = ShoppingCar.objects.filter(usuario=id_user, producto__exact=id_combination)
    if product_shoping_car.exists():
        product_shoping_car.delete()


def search_combination(id_product, type_account):
    type_account_suscription = get_name_console_suscription(type_account)
    combination = GameDetail.objects.filter(producto=id_product,
                                            consola=type_account_suscription,
                                            stock__gt=0)
    if combination.exists():
        return combination.first().id_game_detail
    return 0


def send_email_notification(user_id, message_html):
    email_to = User.objects.filter(pk=user_id).first().email
    soup = BeautifulSoup(settings.EMAIL_FOR_SALE, features="html.parser")
    extra_soup = BeautifulSoup(message_html, 'html.parser')
    body = soup.find("div", {"id": "body"})
    body.append(extra_soup)
    SendEmail().__int__(str(soup), settings.SUBJECT_EMAIL_FOR_SALE, email_to)


def build_div_html(product, combination, account_selected):
    string_pass = account_selected.password
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
                        <b>Usuario:</b><br> {account_selected.cuenta}
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


def check_products_expired():
    products_expired = SaleDetail.objects.filter(fecha_vencimiento__lt=date.today())
    for product in products_expired:
        SaleDetail.objects.filter(pk=product.id_sale_detail).update(fecha_vencimiento=None)
        Products.objects.filter(pk=product.producto.id_product).update(stock=F('stock') + 1)
        GameDetail.objects.filter(pk=product.combinacion.id_game_detail).update(stock=F('stock') + 1)

        account = ProductAccounts.objects.filter(pk=product.cuenta.id_product_accounts)
        if not account.first().activa:
            account.update(activa=True)


def get_duration_account(product_account):
    durations = []
    for i in product_account.values("dias_duracion"):
        item = i["dias_duracion"]
        durations += [item]
    return durations


def get_type_account_suscription(type_account):
    type_account_suscription = TypeSuscriptionAccounts.objects.filter(pk=type_account).values().first()
    if "Cuenta" in type_account_suscription.get("descripcion"):
        type_account_result = 1
    else:
        type_account_result = 2

    return type_account_result


def get_name_console_suscription(type_account):
    type_account_suscription = TypeSuscriptionAccounts.objects.filter(pk=type_account).values().first()
    if "Pc" in type_account_suscription.get("descripcion"):
        return Consoles.objects.filter(descripcion__contains="Pc").first()
    return Consoles.objects.filter(descripcion__contains="xbox").first()


def get_name_licencia_suscription(type_account):
    type_account_suscription = TypeSuscriptionAccounts.objects.filter(pk=type_account).values().first()
    if "Cuenta" in type_account_suscription.get("descripcion"):
        return [Licenses.objects.filter(descripcion="Primaria").values().first().get("id_license"),
                Licenses.objects.filter(descripcion="Secundaria").values().first().get("id_license")]
    return [Licenses.objects.filter(descripcion__contains="digo").values().first().get("id_license")]
