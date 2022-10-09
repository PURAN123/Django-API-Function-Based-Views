
from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
  password = serializers.CharField(write_only=True)
  class Meta:
    model= User
    fields=(
      "id", "username", "first_name", "last_name", "email", "phone", "dob", "zipcode", "street", "city", "state", "country", "password"
    )


class LoginSerializer(serializers.Serializer):
  username = serializers.CharField()
  password = serializers.CharField( write_only=True)


class ChangePasswordSerializer(serializers.Serializer):
  username= serializers.CharField()
  old_password = serializers.CharField()
  new_password = serializers.CharField()
  confirm_password = serializers.CharField()#style={'input_type': 'password'}


class ResetPasswordSerializer(serializers.Serializer):
  email = serializers.EmailField();

class ResetNewPasswordSerializer(serializers.Serializer):
  new_password = serializers.CharField()
  confirm_password = serializers.CharField()