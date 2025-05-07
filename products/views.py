import json
from datetime import date, timedelta

import requests
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import connection
from django.db.models import F, Sum, Min
from django.http import HttpResponse, JsonResponse, HttpResponseServerError
from django.core.cache import cache
from django.shortcuts import redirect
from django.utils.timezone import now
from django.db.models.functions import Lower
from django.views.decorators.csrf import csrf_exempt
from django.contrib.postgres.search import TrigramSimilarity
from unidecode import unidecode

from ecommerceHardcoregamesBack import settings
from products.AdapterEpaycoApi import AdapterEpaycoApi
from products.managePriceFile import ManegePricesFile
from products.models import Products, ShoppingCar, Licenses, Consoles, \
    TypeGames, GameDetail, ProductAccounts, SaleDetail, DaysForRentail, PriceForSuscription, TypeAccounts, \
    VariablesSistema, TypeSuscriptionAccounts, Transactions
from products.productSerializers import ProductsSerializer, ProductSerializer, ShoppingCarSerializer, \
    SerializerForTypes, SerializerGameDetail, SerializerForConsole, SerializerSales, SerializerLicencesName, \
    SerializerDaysForRentail, SerializerPriceSuscriptionProduct, SerializerForVariables
from users.models import User_Customized
from utils.SendEmail import SendEmail
from utils.getJsonFromRequest import GetJsonFromRequest
from django.core.cache import cache
import datetime
import hashlib
import logging
import base64
import hmac

logger = logging.getLogger(__name__)

def get_all_products(request):
    if request.method == "GET":
        size = request.GET.get('size')
        page = request.GET.get('page')
        cache_key = f"all_products_{size}_{page}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return JsonResponse(cached_data)

        all_products = Products.objects.order_by("pk")
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

        payload = {'message': 'proceso exitoso', 'data': serializer.data, 'total_items': count_rows,
                   'code': '00', 'status': 200}
        for i in serializer.data:
            stock = GameDetail.objects.filter(producto=i['pk'],
                                              stock__gt=0).aggregate(Sum('stock'))['stock__sum']
            product_price = GameDetail.objects.filter(producto=i['pk'],
                                              stock__gt=0,
                                              licencia=1).first()
            i['stock'] = 0 if stock is None else stock
            i['price'] = 0 if product_price is None else product_price.precio
        cache.set(cache_key, payload)
        return HttpResponse(JsonResponse(payload), content_type="application/json")


def get_favorite_products(request):
    if request.method == "GET":
        size = request.GET.get('size')
        page = request.GET.get('page')
        cache_key = f"favorite_products_{size}_{page}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return JsonResponse(cached_data)
        all_products = Products.objects.filter().order_by('pk')
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
            product_price = get_lower_price(i['pk'])
            i['stock'] = 0 if stock is None else stock
            i['price'] = get_lowest_price_by_product(i['pk'])
        payload = {
            'message': 'Proceso exitoso',
            'data': serializer.data,
            'total_items': count_rows,
            'code': '00',
            'status': 200
        }
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
        all_products = Products.objects.filter(destacado=True).order_by('-pk')
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
            product_price = get_lower_price(i['pk'])
            i['stock'] = 0 if stock is None else stock
            i['price'] = 0 if product_price is None else product_price
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

        all_products = Products.objects.filter().order_by('-date_last_modified')
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
            product_price = get_lower_price(i['pk'])
            i['stock'] = 0 if stock is None else stock
            i['price'] = 0 if product_price is None else product_price
        payload = {'message': 'proceso exitoso', 'data': serializer.data, 'total_items': count_rows,
                   'code': '00', 'status': 200}
        # Cache the result
        cache.set(cache_key, payload)
        return HttpResponse(JsonResponse(payload), content_type="application/json")


def get_products_by_id(request, id_product):
    if request.method == "GET":
        product = Products.objects.filter(pk=id_product)
        prices_game = (GameDetail.objects.filter(producto=id_product,precio__gt=0)
                       .first())
        if product.exists() and prices_game is not None:

            serializer = ProductSerializer(product, many=True)
            serializer.data[0]['precio_descuento'] = prices_game.precio_descuento
            serializer.data[0]['price'] = prices_game.precio
            serializer.data[0]['stock'] = GameDetail.objects.filter(producto=id_product,
                                                                    stock__gt=0).aggregate(Sum('stock'))['stock__sum']
            payload = {'message': 'proceso exitoso', 'data': serializer.data[0], 'code': '00', 'status': 200}
            return HttpResponse(JsonResponse(payload), content_type="application/json")
        payload = {'message': 'producto no existente', 'data': [], 'code': '00', 'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")


def find_product_by_name(request, name_product):
    if request.method == "GET":
        if name_product and name_product.lower() != "null":
            normalized_name = unidecode(name_product.lower())  # Remove accents
            print(normalized_name)
            product = Products.objects.annotate(
                normalized_title=Lower("title")
            ).filter(
                normalized_title__icontains=normalized_name
            ) | Products.objects.annotate(
                normalized_title=Lower("title")
            ).filter(
                normalized_title__icontains=normalized_name.replace(" ", "")
            )

            if product.exists():
                serializer = ProductSerializer(product, many=True)
                payload = {'message': 'proceso exitoso', 'data': serializer.data, 'code': '00', 'status': 200}
                return JsonResponse(payload, safe=False)

        payload = {'message': 'producto no existente', 'data': [], 'code': '00', 'status': 200}
        return JsonResponse(payload, safe=False)


def get_products_by_type_console(request, id_console):
    if request.method == "GET":
        console = Consoles.objects.filter(pk=id_console)
        product = Products.objects.filter(consola__in=console).exclude(consola__isnull=True)
        if product.exists():
            serializer = ProductSerializer(product, many=True)
            payload = {'message': 'proceso exitoso', 'data': serializer.data, 'code': '00', 'status': 200}
            return HttpResponse(JsonResponse(payload), content_type="application/json")
        payload = {'message': 'producto no existente', 'data': [], 'code': '00', 'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")


@csrf_exempt
def filter_product(request, ):
    if request.method == "POST":
        json_request = json.loads(request.body)
        id_console = json_request['id_console']
        id_category = json_request['id_category']
        range_min = json_request['range_min'] or 0
        range_max = json_request['range_max'] or  0
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

            product = Products.objects.filter(tipo_juego=id_category).order_by("pk")
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

            product = Products.objects.filter(consola=id_console, tipo_juego=id_category).order_by("pk")
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

            product_inventory = GameDetail.objects.filter(
                precio__gte=range_min,
                precio__lt=range_max
            ).values('producto')
            product = Products.objects.filter(consola=id_console,
                                              tipo_juego=id_category,
                                              pk__in=product_inventory
                                              ).order_by("pk")
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

            product_inventory = GameDetail.objects.filter(
                precio__gte=range_min,
                precio__lt=range_max
            ).values('producto')
            product = Products.objects.filter(consola=id_console,
                                              pk__in=product_inventory).order_by("pk")
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

            product_inventory = GameDetail.objects.filter(
                precio__gte=range_min,
                precio__lt=range_max
            ).values('producto')
            product = Products.objects.filter(tipo_juego=id_category,
                                              pk__in=product_inventory).order_by("pk")
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

            product_inventory = GameDetail.objects.filter(
                precio__gte=range_min,
                precio__lt=range_max
            ).values('producto')
            product = Products.objects.filter(pk__in=product_inventory).order_by("pk")
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

        payload = {'message': 'producto no existente', 'data': [], 'code': '00', 'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")


def get_products_by_type_game(request, id_type_game):
    if request.method == "GET":
        cache_key = "products_by_type_game"
        cached_data = cache.get(cache_key)
        if cached_data:
            return JsonResponse(cached_data)

        product = Products.objects.filter(tipo_juego=id_type_game,)
        if product.exists():
            serializer = ProductSerializer(product, many=True)
            payload = {'message': 'proceso exitoso',
                       'data': serializer.data,
                       'code': '00',
                       'status': 200}
            cache.set(cache_key, payload, timeout=259200)
            return HttpResponse(JsonResponse(payload), content_type="application/json")
        payload = {'message': 'producto no existente', 'data': [], 'code': '00', 'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")


def get_products_by_range_price(request):
    if request.method == "GET":
        range_min = request.GET['range_min']
        range_max = request.GET['range_max']
        inventory_products = GameDetail.objects.filter(precio__gt=range_min, precio__lte=range_max, stock__gt=0)
        pk_list = inventory_products.values_list('producto', flat=True)
        product = Products.objects.filter(pk__in=pk_list)
        if product.exists():
            serializer = ProductSerializer(product, many=True)
            payload = {'message': 'proceso exitoso', 'data': serializer.data, 'code': '00', 'status': 200}
            return HttpResponse(JsonResponse(payload), content_type="application/json")
        payload = {'message': 'producto no existente', 'data': [], 'code': '00', 'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")


def price_suscription_product(request, id_product, type_account):
    if request.method == "GET":
        id_type_account_req = TypeSuscriptionAccounts.objects.filter(pk=type_account).first()
        #console_name = get_name_console_suscription(type_account)

        license_name = get_name_licencia_suscription(type_account)
        stock_for_product = GameDetail.objects.filter(
            producto=id_product,
            #consola__in=console_name,
            licencia__in=license_name,
            stock__gt=0
        )

        if not stock_for_product.exists():
            payload = {'message': 'producto no existente', 'data': [], 'code': '00', 'status': 200}
            return HttpResponse(JsonResponse(payload), content_type="application/json")

        if ("cuenta" in id_type_account_req.__str__().lower()
            or "pc" in id_type_account_req.__str__().lower()
            or "consola" in id_type_account_req.__str__().lower()):
            type_account_sale = 1
        else:
            type_account_sale = 2


        product_accounts = ProductAccounts.objects.filter(producto=id_product,
                                                          tipo_cuenta=type_account_sale,
                                                          activa=True)
        duration_account = get_duration_account(product_accounts)

        product = PriceForSuscription.objects.filter(producto=id_product,
                                                     estado=True,
                                                     duracion_dias_alquiler__in=duration_account,
                                                     tipo_producto__in=[type_account],
                                                     stock__gt = 0,
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
        product_type = Products.objects.filter(pk=id_product).first().type_id.id_product_type
        combination = GameDetail.objects.filter(producto=id_product, stock__gt=0, precio__gt=0)

        if combination.exists():
            serializer = SerializerGameDetail(combination, many=True)
            payload = {'message': 'proceso exitoso', 'product_id': id_product,
                       "product_type": product_type, 'data': serializer.data,
                       'code': '00', 'status': 200}
            return HttpResponse(JsonResponse(payload), content_type="application/json")
        payload = {'message': 'proceso exitoso', 'data': [], 'code': '00', 'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")


def licence_by_product(request, id_product, id_console):
    if request.method == "GET":
        combination = GameDetail.objects.filter(producto=id_product,
                                                consola=id_console,
                                                #licencia__in=type_account_list,
                                                stock__gt=0).order_by('producto', 'consola', 'licencia',
                                                                      'stock').distinct()
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
        payload = {'message': 'producto no existente o usuario no existente', 'data': [], 'code': '00', 'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")


def get_shopping_car(request):
    if request.method == "GET":
        user_id = request.GET['user_id']
        user = ShoppingCar.objects.filter(usuario=user_id, producto__stock__gt=0)
        state = True if request.GET['state'] == "true" else False
        if user.exists():
            if state:
                shopping_cars = ShoppingCar.objects.filter(usuario=user_id, estado=state,
                                                           producto__stock__gt=0).order_by('pk')
            else:
                shopping_cars = ShoppingCar.objects.filter(usuario=user_id, producto__stock__gt=0).order_by('pk')
            print(shopping_cars)
            shopping_cars_serialized = ShoppingCarSerializer(shopping_cars, many=True)
            payload = {'message': 'proceso exitoso', 'user_id': int(user_id),
                       'data': shopping_cars_serialized.data, 'code': '00', 'status': 200}
            return HttpResponse(JsonResponse(payload), content_type="application/json")
        payload = {'message': 'producto no existente o usuario no existente', 'data': [], 'code': '00', 'status': 200}
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
        type_account_available = PriceForSuscription.objects.filter(stock__gt=0).values_list('tipo_producto', flat=True)
        type_account = TypeSuscriptionAccounts.objects.filter(pk__in=type_account_available)
        serializer = SerializerForTypes(type_account, many=True)
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
    try:
        json_request = json.loads(request)
        id_user = json_request['id_user']
        user = User.objects.filter(pk=id_user).first()
        message_html = ""

        for item in json_request['data']:

            combination_selected:GameDetail = GameDetail.objects.filter(pk=item['id_combination']).first()
            name_console:str = combination_selected.consola.descripcion
            account_selected = combination_selected.cuenta
            item['days_rentail'] = combination_selected.duracion_dias_alquiler

            if combination_selected:
                product_selected = combination_selected.producto
                if user and not user.is_superuser:
                    combination_selected.stock = F('stock') - 1
                    create_sale(item, id_user, account_selected)
                    update_points_sale(id_user, product_selected.puntos_venta)
                    delete_shopping_product(item['id_combination'], id_user)
                    combination_selected.save()
                message_html += build_div_html(product_selected, combination_selected, account_selected, name_console)
                send_email_notification(id_user, message_html)
            else:
                global_exception_handler(request, None)
                return False

        return True
    except Exception as e:
        send_email = True
        global_exception_handler(request, e, send_email)
        return False

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
        payload = {'message': 'producto no existente o usuario no existente', 'data': [], 'code': '00', 'status': 200}
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
        payload = {'message': 'producto no existente o usuario no existente', 'data': [], 'code': '00', 'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")


@csrf_exempt
def delete_product_shopping_car(request, shooping_car_id):
    if request.method == "DELETE":
        shooping_car = ShoppingCar.objects.filter(pk=shooping_car_id)
        if shooping_car.count() > 0:
            ShoppingCar.objects.filter(pk=shooping_car_id).delete()
            payload = {'message': 'proceso exitoso', 'code': '00', 'status': 200}
            return HttpResponse(JsonResponse(payload), content_type="application/json")
        payload = {'message': 'producto no existente', 'data': [], 'code': '00', 'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")


def sendEmail(request):
    # check_products_expired()
    send_email_notification(2, "<html><head>prueba</head><body>prueba</body></html>")
    return HttpResponse(JsonResponse({'message': "prueba email", "status": 200, "code": "00"}),
                        content_type="application/json")


@csrf_exempt
def manageFile(request):
    #ManegePricesFile()
    confirm_sale(request.body)
    return HttpResponse(JsonResponse({'message': 'File procesado', "status": 200, "code": "00"}),
                        content_type="application/json")


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


def search_combination(id_product, type_account, days_rentail):
    #solo aplica para productos de suscripcion
    type_account_suscription = get_name_console_suscription(type_account)
    licence_name = get_name_licencia_suscription(type_account)
    combination = GameDetail.objects.filter(producto=id_product,
                                            consola=type_account_suscription,
                                            duracion_dias_alquiler = days_rentail,
                                            licencia__in=licence_name,
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


def build_div_html(product, combination, account_selected, name_console):
    string_pass = account_selected.password
    if string_pass is None:
        string_pass = ""
    return f'''<div style="margin-bottom: 20%;">
               <h3>{product.title}</h3>
               <div style="margin-bottom: auto;">
                  <div style="float:right;font-weight:600;font-size:16px;">
                     <img src="{product.image}" width="30" class="CToWUd" data-bit="iit">
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
                        <b>Licencia:</b> {combination.licencia}
                     </lu>
                  </li>
                  <li>
                     <lu>
                        <b>Consola:</b> {name_console if name_console is not None else str(combination.consola).capitalize()}
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
    for i in product_account:
        exist_game_detail = GameDetail.objects.filter(producto_id=i.producto.id_product, duracion_dias_alquiler=i.dias_duracion).exists()
        if exist_game_detail and durations.count(i.dias_duracion) == 0:
            durations += [i.dias_duracion]
    return durations


def get_type_account_suscription(type_account):
    type_account_suscription = TypeSuscriptionAccounts.objects.filter(pk=type_account).values().first()
    if ("cuenta" in type_account_suscription.get("descripcion").lower() or
        "consola" in type_account_suscription.get("descripcion").lower() or
        "pc" in type_account_suscription.get("descripcion").lower()):
        type_account_result = 1
    else:
        type_account_result = 2

    return type_account_result


def get_name_console_suscription(type_account):
    #buscar el tipo de consola que se va a comprar de acuerdo al tipo de cuenta de suscripcion
    return Consoles.objects.filter(descripcion__contains="xbox").first()


def get_name_licencia_suscription(type_account):
    type_account_suscription = TypeSuscriptionAccounts.objects.filter(pk=type_account).values().first()
    if ("consola" in type_account_suscription.get("descripcion").lower()):
        return [Licenses.objects.filter(descripcion="Primaria").values().first().get("id_license"),
                Licenses.objects.filter(descripcion="Secundaria").values().first().get("id_license")]
    if ("pc" in type_account_suscription.get("descripcion").lower()):
        return [Licenses.objects.filter(descripcion__icontains="pc").values().first().get("id_license")]
    return [Licenses.objects.filter(descripcion__contains="digo").values().first().get("id_license")]

def confirm_sale_get(request):
    if request.method == "GET":
        token = request.GET.get('token')
        if validate_token(token):
            console_id = convert_console_name(request.GET.get('console').rstrip().lower())
            product_selected = Products.objects.filter(pk=request.GET.get('id_product').rstrip())
            license = Licenses.objects.filter(pk=request.GET.get('id_licencia').strip())
            account = ProductAccounts.objects.filter(cuenta__iexact=request.GET.get('account').rstrip())
            console = Consoles.objects.filter(pk=console_id)
            days_retail = request.GET.get('days_rentail').rstrip() if request.GET.get('days_rentail').rstrip() != 'null' else 0
            combination_selected = GameDetail.objects.filter(producto=product_selected.first(),
                                                             consola=console.first(),
                                                             licencia=license.first(),
                                                             duracion_dias_alquiler = days_retail,
                                                             stock__gt=0
                                                             ).first()
            sale = {}
            if not combination_selected or not product_selected.exists() :
                payload = {'message': 'producto no existente',
                           'code': '00',
                           'status': 200}
                return HttpResponse(JsonResponse(payload), content_type="application/json")

            if not account.exists():
                payload = {'message': 'cuenta no existente',
                           'code': '00',
                           'status': 200}
                return HttpResponse(JsonResponse(payload), content_type="application/json")

            combination_selected.stock = F('stock') - 1
            sale['id_combination'] = combination_selected.id_game_detail
            combination_selected.save()

            check_account_stock(combination_selected, account)
            sale['is_rentail'] = request.GET.get('is_rentail')
            sale['days_rentail'] = days_retail
            create_sale(sale, 1, account.first())
            payload = {'message': 'se ha actualizado el stock satisfactoriamente!!!', 'data': [], 'code': '00', 'status': 200}
            return HttpResponse(JsonResponse(payload), content_type="application/json")

        payload = {'message': 'token invalido', 'data': [], 'code': '00', 'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")
def validate_token(token):
    return token == settings.TOKEN_CONFIRM_SALE

def convert_console_name(console_name):
    console_name = console_name.replace(" ", "").lower()
    if console_name == "ps4":
        return 1
    elif console_name == "ps5":
        return 2
    elif console_name == "xbox":
        return 5
    else:
        return 6

def convert_name_type_suscription_account(type_name):
    type_name = type_name.replace(" ", "").lower()
    if type_name == "xbox":
        return 3
    if type_name == "codigo":
        return 2
    if type_name == "pc":
        return 1

def check_account_stock(product_selected, account):
    count_stock = GameDetail.objects.filter(pk=product_selected.pk,
                                            stock__gt=1).count()
    if count_stock < 1:
        account.update(activa=False)

def update_stock(product_selected):
    sum_stocks = GameDetail.objects.filter(producto=product_selected.first().pk,
                                           stock__gt=0).aggregate(Sum('stock'))
    product_selected.update(stock=sum_stocks['stock__sum'])


@csrf_exempt
def request_api_epayco(request):
    ref_payco = request.GET.get('ref_payco') if request.GET.get('ref_payco') is not None \
        else get_transaction_saved(request)
    x_ref_epayco = request.GET.get('x_ref_payco')
    if ref_payco is not None or x_ref_epayco is not None:
        if ref_payco is not None:
            adapter = AdapterEpaycoApi()
            response = adapter.request_get(ref_payco)
            success_value = response.get('success')
            is_accepted = (response.get('data', {}).get('x_transaction_state') or "").lower() == "aceptada"
            confirm_sale_body = response.get('data').get('x_extra7')
            is_pending = (response.get('data', {}).get('x_transaction_state') or "").lower() == "pendiente"
            if is_pending:
                response["data"]["x_id_invoice"] = request.GET.get("x_id_factura", "x_id_invoice")
                save_transaction(response, ref_payco)
                return redirect(settings.PENDING_URL)
        else:
            success_value = (request.GET.get("x_response") or "").lower() == "aceptada"
            is_accepted = (request.GET.get('x_transaction_state') or "").lower() == "aceptada"
            confirm_sale_body = request.GET.get('x_extra7')
            ref_payco = x_ref_epayco if ref_payco is None else ref_payco
            response = {
                "data": {
                    "x_amount": request.GET.get('x_amount'),
                    "x_bank_name": request.GET.get('x_bank_name'),
                    "ref_payco": ref_payco,
                    "x_id_invoice": request.GET.get('x_id_invoice'),
                    "x_extra6": request.GET.get('x_extra6'),
                    "x_extra7": request.GET.get('x_extra7'),
                    "x_transaction_state": request.GET.get('x_transaction_state') or ""
                }
            }
        exist_transaction = save_transaction(response, ref_payco)

        if not exist_transaction:
            return redirect(settings.CONFIRMATION_URL)

        if success_value is not None and is_accepted:
            if confirm_sale(confirm_sale_body):
                return redirect(settings.CONFIRMATION_URL)
            else:
                return redirect(settings.DECLINED_URL)

    return redirect(settings.DECLINED_URL)

def check_for_disable_account(product):
    if (GameDetail.objects.filter(cuenta=product.first().cuenta, stock__gt=0)
            .count() == 0):
        return True

    return False
    
def global_exception_handler(request, exception, send_email=False):
    if send_email:
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        message_html = f"<html><head>Ha ocurrido un error en una compra </head><body>{exception} con el request: <br> {body_data}</body></html>"
        SendEmail().__int__(message_html, "Ha ocurrido un error", settings.FROM_EMAIL)

def save_transaction(response, ref_payco):
    id_invoice = response.get('data').get('x_id_invoice')
    status = response.get('data', {}).get('x_transaction_state', "").lower()


    if Transactions.objects.filter(id_invoice=id_invoice).exists():
        Transactions.objects.filter(ref_payco=ref_payco).update(ref_payco=ref_payco,
                                                                status=status)
        return False

    extra7_param = response.get("data", {}).get("x_extra7")
    if extra7_param:
        try:
            extra7_data = json.loads(extra7_param)
        except json.JSONDecodeError:
            extra7_data = {}
    else:
        extra7_data = {}
    id_user = extra7_data.get('id_user', None)

    try:
        Transactions(
            status=status,
            amount=response.get('data', {}).get('x_amount') or 0,
            payment_id=(response.get('data', {}).get('x_bank_name') or "").lower(),
            ref_payco=ref_payco,
            id_invoice=id_invoice,
            user_id=User.objects.filter(pk=id_user).first(),
        ).save()
    except Exception as e:
        print(f"An error occurred while saving the transaction: {e}")

    return True

def get_transaction_saved(request):
    id_invoice = request.GET.get('x_id_invoice')
    transaction = Transactions.objects.filter(id_invoice=id_invoice).first()
    if transaction is not None:
        return transaction.ref_payco
    return None

def clear_cache(request):
    if request.method == "GET":
        cache.clear()
        payload = {'message': 'cache cleared', 'code': '00', 'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")

def confirm_sale_bold(request):
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    order_id = request.GET.get('bold-order-id')
    status = request.GET.get('bold-tx-status')

    if not all([order_id, status]):
        return JsonResponse({"error": "Missing required fields"}, status=400)

    transaction = Transactions.objects.filter(ref_payco=order_id).first()
    if transaction:
        transaction.status = status
        transaction.save()
        if status == "approved":
            confirm_sale(transaction.request)
            return redirect(settings.CONFIRMATION_URL)
        return redirect(settings.DECLINED_URL)

    return JsonResponse({"error": "Transaction not found"}, status=404)

@csrf_exempt
def bold_webhook(request):
    logger.info("Received a request at bold_webhook")

    if request.method != "POST":
        logger.warning("Invalid request method: %s", request.method)
        return JsonResponse({"error": "Method not allowed"}, status=405)

    signature = request.headers.get("x-bold-signature", "")
    body = request.body

    logger.debug("Request body: %s", body)
    logger.debug("Received signature: %s", signature)

    encoded_body = base64.b64encode(body)
    secret_key = settings.SECRET_KEY_BOLD.encode()
    hashed = hmac.new(secret_key, encoded_body, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(hashed, signature):
        logger.error("Signature validation failed")
        return JsonResponse({"error": "Invalid signature"}, status=400)

    logger.info("Signature validation succeeded")

    response = JsonResponse({"message": "Event received successfully"}, status=200)

    try:
        data = json.loads(body)
        logger.info("Parsed request data: %s", data)
        process_bold_event(data)
    except json.JSONDecodeError as e:
        logger.error("Failed to parse JSON: %s", e)
    except Exception as e:
        logger.exception("Error processing event: %s", e)

    logger.info("bold_webhook processing completed")
    return response

def process_bold_event(data):
    event_type = data.get("type")
    franchise = data.get("data", {}).get("card", {}).get("franchise")
    transaction_id = data.get("data", {}).get("metadata", {}).get("reference")

    if event_type == "SALE_APPROVED":
        transaction = Transactions.objects.filter(ref_payco=transaction_id).first()
        if transaction and transaction.status != "approved":
            logger.info("Processing SALE_APPROVED event for transaction: %s", transaction_id)
            transaction.status = "approved"
            transaction.payment_id = franchise
            transaction.save()

            request_data = transaction.request
            confirm_sale(request_data)

        elif transaction.status == "approved":
            logger.info("Transaction already approved: %s", transaction_id)
            transaction.payment_id = franchise
            transaction.save()

@csrf_exempt
def generate_hash_bold(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    data = parse_request_data(request)
    if not data:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    amount = data.get('amount')
    currency = data.get('currency')
    request_transaction = data.get('request_transaction')

    if not all([amount, currency, request_transaction]):
        return JsonResponse({"error": "Missing required fields"}, status=400)

    order_id = generate_order_id()
    signature = generate_signature(order_id, amount, currency, settings.SECRET_KEY_BOLD)

    create_transaction_record(order_id, amount, request_transaction)

    payload = build_payload(order_id, signature)
    return JsonResponse(payload, status=200)

def parse_request_data(request):
    try:
        return json.loads(request.body)
    except json.JSONDecodeError:
        return None

def generate_signature(order_id, amount, currency, secret_key):
    linked_string = f"{order_id}{amount}{currency}{secret_key}"
    m = hashlib.sha256()
    m.update(linked_string.encode())
    return m.hexdigest()

def create_transaction_record(order_id, amount, request_transaction):
    user_id = json.loads(request_transaction)["id_user"]
    return Transactions.objects.create(
        status="pendiente",
        amount=amount,
        payment_id="bold",
        ref_payco=order_id,
        id_invoice=order_id,
        request=request_transaction,
        user_id=User.objects.filter(pk=user_id).first()
    )

def build_payload(order_id, signature):
    return {
        'apiKey': settings.API_KEY_BOLD,
        'integritySignature': signature,
        'orderId': order_id,
        'redirectionUrl': settings.REDIRECTION_URL_BOLD,
        'code': '00',
        'status': 200
    }

def get_lower_price(pk,):
    lower_price = GameDetail.objects.filter(
        producto=pk,
        stock__gt=0,
    ).aggregate(Min('precio'))
    return lower_price['precio__min']


def generate_order_id():
    now = datetime.datetime.now()
    timestamp = int(now.timestamp() * 1000)
    order_id = f"inv_{timestamp}"

    return order_id

def get_lowest_price_by_product(product_id):
    lowest_price = (GameDetail.objects.filter(producto_id=product_id, stock__gt=0, precio__gt=0)
                    .aggregate(Min('precio')))
    return lowest_price['precio__min'] or 0