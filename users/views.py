import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from users.models import User_Customized, TypeDocument
from utils.getJsonFromRequest import GetJsonFromRequest
from utils.joinModels import JoinModels



# Create your views here.
def get_all_users(request):
    all_users = User.objects.all()
    response = serializers.serialize("json", all_users)
    payload = {'message': 'proceso exitoso', 'response': json.loads(response), 'code': '00', 'status': 200}

    return HttpResponse(JsonResponse(payload), content_type='application/json')


@csrf_exempt
def get_user_by_email(request, self=None):
    if request.method == "POST":
        body = GetJsonFromRequest.__int__(self, request)
        email = body['email']
        user_selected = User.objects.filter(username=email)
        if user_selected.exists():
            user_customized_selected = User_Customized.objects.filter(username=email)
            models_joined = JoinModels.__int__(self, user_selected, user_customized_selected)
            payload = {"fields": models_joined, 'message': 'proceso exitoso', 'code': '00', 'status': 200}
            return HttpResponse(JsonResponse({'data': payload}), content_type='application/json')

        return HttpResponse(JsonResponse({'message': "usuario no existe", 'status': 200, 'code': '01'}),
                            content_type="application/json")


@csrf_exempt
def get_user_by_id(request, id_user, self=None):
    if request.method == "GET":
        id_user = id_user
        user_selected = User.objects.filter(id=id_user)
        if user_selected.exists():
            user_customized_selected = User_Customized.objects.filter(user_id=id_user)
            models_joined = JoinModels.__int__(self, user_selected, user_customized_selected)
            payload = {"fields": models_joined, 'message': 'proceso exitoso', 'code': '00', 'status': 200}
            return HttpResponse(JsonResponse({'data': payload}), content_type='application/json')

        return HttpResponse(JsonResponse({'data': {}, 'status': 200, 'code': '01', 'message': 'el usuario no existe'}),
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
        id_document = body['id_document']
        type_id_document = body['type_id_document']
        avatar = body['avatar']

        exist_user = User.objects.filter(username=email).exists()
        if exist_user:
            return HttpResponse(
                JsonResponse({'message': 'ya esxiste un usuario con este email', "status": 200, "code": "01"}),
                content_type="application/json")
        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=email,
            email=email,
            password=password
        )

        user.save()
        last_user_id = User.objects.last().id
        type_id_selected = TypeDocument.objects.get(type_id=type_id_document)
        user_customized = User_Customized(user_id=last_user_id,
                                          phone_number=phone_number,
                                          id_document=id_document,
                                          type_id_document=type_id_selected,
                                          avatar=avatar
                                          )
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
            user_customized_selected = User_Customized.objects.filter(user_id=user_selected.get( email=username ))
            models_joined = JoinModels.__int__(self, user_selected, user_customized_selected)
            payload = {"fields": models_joined, 'message': 'proceso exitoso', 'code': '00', 'status': 200}
            return HttpResponse(JsonResponse({'data': payload}), content_type='application/json')

        return HttpResponse(JsonResponse({'message': "usuario no existe", 'status': 200, 'code': '01'}),
                            content_type="application/json")


@csrf_exempt
def logout_request(request):
    user_logout = logout(request)
    if user_logout is not None:
        return HttpResponse(JsonResponse({'message': 'usuario logout'}), content_type="application/json")
    return HttpResponse(JsonResponse({'message': 'no hay usuario', 'status': 200, 'code': '01'}),
                        content_type="application/json")
