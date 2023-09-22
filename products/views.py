import json

from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from products.models import Products, ProductsType
from products.productSerializers import ProductsSerializer
from utils.getJsonFromRequest import GetJsonFromRequest


# Create your views here.
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
