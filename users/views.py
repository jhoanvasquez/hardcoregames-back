import json
import uuid

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from ecommerceHardcoregamesBack import settings
from users.models import User_Customized
from users.userSerializer import UserSerializer, UserResponseSerializer, UserCustomSerializer
from utils.SendEmail import SendEmail
from utils.getJsonFromRequest import GetJsonFromRequest
from utils.joinModels import JoinModels


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
            serializer = UserResponseSerializer(user_selected, many=True)
            serializer_user_custom = UserCustomSerializer(user_customized_selected, many=True)
            payload = {"fields": serializer.data[0], "other_fields": serializer_user_custom.data[0],
                       'message': 'proceso exitoso', 'code': '00', 'status': 200}
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
        user_customized = User_Customized(user_id=last_user_id,
                                          phone_number=phone_number,
                                          avatar=avatar
                                          )
        user_customized.save()
        return HttpResponse(JsonResponse({'message': 'usuario registrado exitosamente', "status": 200,
                                          "code": "00", "user_id": last_user_id}), content_type="application/json")


@csrf_exempt
def login_request(request, self=None):
    if request.method == "POST":
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        username = body['user']
        password = body['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            user_loged = User.objects.filter(username=username)
            serializer = UserSerializer(user_loged, many=True)
            payload = {"fields": serializer.data[0], 'message': 'proceso exitoso', 'code': '00', 'status': 200}
            return HttpResponse(JsonResponse({'data': payload}), content_type='application/json')

        return HttpResponse(JsonResponse({'message': "usuario o contraseña incorrectos", 'status': 200, 'code': '01'}),
                            content_type="application/json")


@csrf_exempt
def logout_request(request):
    user_logout = logout(request)
    if user_logout is not None:
        return HttpResponse(JsonResponse({'message': 'usuario logout'}), content_type="application/json")
    return HttpResponse(JsonResponse({'message': 'no hay usuario', 'status': 200, 'code': '01'}),
                        content_type="application/json")


@csrf_exempt
def update_user(request, self=None):
    if request.method == "POST":
        body = GetJsonFromRequest.__int__(self, request)
        user_id = body['user_id']
        first_name = body['first_name']
        last_name = body['last_name']
        id_document = body['id_document']
        exist_user = User.objects.filter(pk=user_id).exists()
        if exist_user:
            User.objects.filter(pk=user_id).update(first_name=first_name,
                                                   last_name=last_name)
            User_Customized.objects.filter(user_id=user_id).update(id_document=id_document)
            return HttpResponse(
                JsonResponse({'message': 'datos actualizados exitosamente', "status": 200, "code": "00"}),
                content_type="application/json")

        return HttpResponse(JsonResponse({'message': 'usuario no existe', "status": 200, "code": "01"}),
                            content_type="application/json")


@csrf_exempt
def change_password(request, self=None):
    if request.method == "POST":
        body = GetJsonFromRequest.__int__(self, request)
        user_id = body['user_id']
        current_pass = body['current_pass']
        new_pass = body['new_pass']
        exist_user = User.objects.filter(pk=user_id).exists()
        if exist_user:
            user = User.objects.get(pk=user_id)
            is_pass = user.check_password(current_pass)
            if is_pass:
                user.set_password(new_pass)
                user.save()
                return HttpResponse(
                    JsonResponse({'message': 'datos actualizados exitosamente', "status": 200, "code": "00"}),
                    content_type="application/json")
            return HttpResponse(
                JsonResponse({'message': 'datos incorrectos', "status": 200, "code": "01"}),
                content_type="application/json")

        return HttpResponse(JsonResponse({'message': 'usuario no existe', "status": 200, "code": "01"}),
                            content_type="application/json")


@csrf_exempt
def token_pass(request, self=None):
    if request.method == "POST":
        body = GetJsonFromRequest.__int__(self, request)
        username = body['username']
        exist_user = User.objects.filter(username=username).exists()
        subject_email = settings.SUBJECT_EMAIL_FOR_TOKEN
        text_email = settings.EMAIL_FOR_TOKEN
        if exist_user:
            token = str(uuid.uuid4())[0:5]
            text_email += "<center><b>" + token + "</b><center>"
            SendEmail.__int__(self, text_email, subject_email, username)
            return HttpResponse(
                JsonResponse({'token': token, "status": 200, "code": "00"}),
                content_type="application/json")

        return HttpResponse(JsonResponse({'message': 'usuario no existe', "status": 200, "code": "01"}),
                            content_type="application/json")


@csrf_exempt
def set_password(request, self=None):
    if request.method == "POST":
        body = GetJsonFromRequest.__int__(self, request)
        username = body['username']
        new_pass = body['new_password']
        exist_user = User.objects.filter(username=username).exists()
        if exist_user:
            user = User.objects.get(username=username)
            user.set_password(new_pass)
            user.save()
            return HttpResponse(
                JsonResponse({'message': "constraseña actualizada exitosamente", "status": 200, "code": "00"}),
                content_type="application/json")
        return HttpResponse(JsonResponse({'message': 'usuario no existe', "status": 200, "code": "01"}),
                            content_type="application/json")
