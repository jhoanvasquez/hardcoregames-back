import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

import users
from users.models import User_Customized
from utils.getJsonFromRequest import GetJsonFromRequest
import jwt


# Create your views here.
def get_all_users(request):
    all_users = User.objects.all()
    response = serializers.serialize("json", all_users)
    payload = {'message': 'proceso exitoso', 'response': json.loads(response), 'code': '00', 'status': 200}
    response_encrypt = jwt.encode({"response": payload}, 'prueba-secret')

    return HttpResponse(JsonResponse({"token": response_encrypt}), content_type='application/json')


@csrf_exempt
def get_user_by_email(request, self=None):
    if request.method == "POST":
        body = GetJsonFromRequest.__int__(self, request)
        email = body['email']
        user_selected = User.objects.filter(username=email)
        if user_selected.exists():
            response = serializers.serialize("json", user_selected)
            return HttpResponse(JsonResponse(
                {'message': 'proceso exitoso', 'response': json.loads(response), 'code': '00', 'status': 200}),
                content_type='application/json')
        return HttpResponse(JsonResponse({'message': "usuario no existe", 'status': 200, 'code': '01'}),
                            content_type="application/json")\

@csrf_exempt
def get_user_by_id(request, self=None):
    if request.method == "POST":
        body = GetJsonFromRequest.__int__(self, request)
        id = body['id']
        user_selected = User.objects.filter(id=id)
        if user_selected.exists():
            response = serializers.serialize("json", user_selected)
            response = GetJsonFromRequest.jsonArrToJson(self, response)
            return HttpResponse(JsonResponse(
                {'message': 'proceso exitoso', 'data': json.loads(response), 'code': '00', 'status': 200}),
                content_type='application/json')
        return HttpResponse(JsonResponse({'message': "usuario no existe", 'status': 200, 'code': '01'}),
                            content_type="application/json")


@login_required
def index(request):
    return HttpResponse(JsonResponse({'message': 'index'}), content_type="application/json")


@csrf_exempt
def register(request, self=None):
    if request.method == "POST":
        body = GetJsonFromRequest.__int__(self, request)
        first_name = body['first_name']
        last_name = body['last_name']
        email = body['email']
        password = body['password']
        phone_number = body['phone_number']
        exist_user = User.objects.filter(username=email).exists()
        if exist_user:
            return HttpResponse(
                JsonResponse({'message': 'ya esxiste un usuario con este email', "status": 200, "code": "01"}),
                content_type="application/json")
        user = User.objects.create_user(first_name=first_name, last_name=last_name,
                                        username=email, email=email, password=password)

        user.save()
        last_user_id = User.objects.last().id
        user_customized = User_Customized(user_id=last_user_id, phone_number=phone_number)
        user_customized.save()
        return HttpResponse(JsonResponse({'message': 'usuario registrado exitosamente', "status": 200, "code": "00"}),
                            content_type="application/json")


@csrf_exempt
def login_request(request, self=None):
    if request.method == "POST":
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        username = body['user']
        password = body['password']
        user = authenticate(username=username, password=password)
        user_selected = User.objects.filter(username=username)

        if user is not None:
            login(request, user)
            response = serializers.serialize("json", user_selected)
            response = GetJsonFromRequest.jsonArrToJson(self, response)
            return HttpResponse(JsonResponse({'data': json.loads(response), 'message': 'usuario logeado existosamente', 'code': '00'}),
                                content_type="application/json")
        return HttpResponse(JsonResponse({'message': "usuario no existe", 'status': 200, 'code': '01'}),
                            content_type="application/json")


@csrf_exempt
def logout_request(request):
    user_logout = logout(request)
    if user_logout is not None:
        return HttpResponse(JsonResponse({'message': 'usuario logout'}), content_type="application/json")
    return HttpResponse(JsonResponse({'message': 'no hay usuario', 'status': 200, 'code': '01'}),
                        content_type="application/json")
