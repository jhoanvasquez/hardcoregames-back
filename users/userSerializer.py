from django.contrib.auth.models import User

from rest_framework import serializers

from users.models import User_Customized


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk',)


class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk', 'first_name', 'last_name', 'is_superuser', 'email', 'username')


class UserCustomSerializer(serializers.ModelSerializer):
    class Meta:
        model = User_Customized
        fields = ('phone_number', 'avatar', 'puntos')
