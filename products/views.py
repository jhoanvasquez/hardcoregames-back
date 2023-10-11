import json
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from products.models import Products, ProductsType, Sales, PaymentType, SaleDetail
from products.productSerializers import ProductsSerializer, ProductSerializer
from utils.SendEmail import SendEmail
from utils.getJsonFromRequest import GetJsonFromRequest


@csrf_exempt
def create_sale(request, self=None):
    if request.method == "POST":
        today = date.today()
        body = GetJsonFromRequest.__int__(self, request)
        status_sale = body['status_sale']
        date_sale = body['date_sale']
        payment_id = body['payment_id']
        user_id = body['user_id']
        amount = body['amount']
        payment_type_instance = PaymentType.objects.filter(pk=payment_id).first()
        user_instance = User.objects.filter(pk=user_id).first()
        sale = Sales(
            status_sale=status_sale,
            date_sale=date_sale,
            payment_id=payment_type_instance,
            user_id=user_instance,
            amount=amount,
        )
        sale.save()
        for product in body['products']:
            product_instance = Products.objects.filter(pk=product['product_id']).first()
            sale_instance = Sales.objects.filter(pk=sale.id_sale).first()
            days_enabled_product = product_instance.days_enable
            date_expiration = today + timedelta(days=int(days_enabled_product)) if product_instance.days_enable > 0 else None
            sale_detail = SaleDetail(
                price=product['price'],
                quantity=product['quantity'],
                total_value=product['total_value'],
                date_expiration=date_expiration,
                product_id=product_instance,
                fk_id_sale=sale_instance,
            )
            sale_detail.save()
        return HttpResponse(JsonResponse({'message': 'venta registrada exitosamente', "status": 200, "code": "00"}),
                            content_type="application/json")


@csrf_exempt
def create_product(request, self=None):
    if request.method == "POST":
        body = GetJsonFromRequest.__int__(self, request)
        description = body['description']
        stock = body['stock']
        price = body['price']
        email_for_product = body['email_for_product']
        pass_for_product = body['pass_for_product']
        days_enable = body['days_enable']
        date_register = body['date_register']
        image = body['image']
        type_id_id = body['type_id_id']

        product_type = ProductsType.objects.filter(id_product_type=type_id_id).first()
        product = Products(
            description=description,
            stock=stock,
            price=price,
            email_for_product=email_for_product,
            pass_for_product=pass_for_product,
            days_enable=days_enable,
            date_register=date_register,
            image=image,
            type_id=product_type

        )
        product.save()
        return HttpResponse(JsonResponse({'message': 'producto registrado exitosamente', "status": 200, "code": "00"}),
                            content_type="application/json")


def get_all_products(request):
    if request.method == "GET":
        all_products = Products.objects.all()
        serializer = ProductsSerializer(all_products, many=True)
        payload = {'message': 'proceso exitoso', 'data': serializer.data, 'code': '00', 'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")


def get_favorite_products(request):
    if request.method == "GET":
        all_products = Products.objects.all().order_by('-calification')
        serializer = ProductsSerializer(all_products, many=True)
        payload = {'message': 'proceso exitoso', 'data': serializer.data, 'code': '00', 'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")


def get_news_for_products(request):
    if request.method == "GET":
        all_products = Products.objects.all().order_by('-date_last_modified')
        serializer = ProductsSerializer(all_products, many=True)
        payload = {'message': 'proceso exitoso', 'data': serializer.data, 'code': '00', 'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")


def get_products_by_id(request, id_product):
    if request.method == "GET":

        product = Products.objects.filter(pk=id_product)
        if product.exists():
            serializer = ProductSerializer(product, many=True)
            payload = {'message': 'proceso exitoso', 'data': serializer.data[0], 'code': '00', 'status': 200}
            return HttpResponse(JsonResponse(payload), content_type="application/json")
        payload = {'message': 'producto no existente', 'data': {}, 'code': '00', 'status': 200}
        return HttpResponse(JsonResponse(payload), content_type="application/json")


def sendEmail(request):
    SendEmail().__int__()
    return HttpResponse(JsonResponse({'message': 'Email enviado', "status": 200, "code": "00"}),
                        content_type="application/json")
