import json

from django.contrib.auth.models import User
from django.core import serializers
from django.http import HttpResponse, JsonResponse

import users


# Create your views here.
def get_all_users(request):
    all_users = User.objects.all()
    response = serializers.serialize("json", all_users)
    return HttpResponse(response, content_type='application/json')

def detail(request, question_id):
    return HttpResponse("You're looking at question %s." % question_id)
