from django.contrib.auth import login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_auth.serializers import LoginSerializer
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.utils.http import base36_to_int, int_to_base36

from .models import User
from .tokens import generate_token
from .serializer import (ChangePasswordSerializer, LoginSerializer,
                         ResetNewPasswordSerializer, ResetPasswordSerializer,
                         UserSerializer)


@api_view(["GET"])
def api_root(request):
  return Response({
    "users":reverse("users", request=request),
    "create_user": reverse("create_user", request=request)
  })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def all_users(request):
  """
  Access individual user data. If you are super user then you can
  access all user data. If you are active user then youcan view or update only
  your own data.
  """
  if(request.user.is_superuser):
    user = User.objects.all()
    page = PageNumberPagination()
    page.page_size = 3
    result_page = page.paginate_queryset(user, request)
    serializer = UserSerializer(result_page, many= True)
    return page.get_paginated_response(serializer.data)
  if(request.user.is_authenticated):
    user = User.objects.get(pk=request.user.id)
    serializer = UserSerializer(user)
    return Response(serializer.data,status=status.HTTP_200_OK)
  else:
    return Response({"details": "Authentication credentials were not provided."}, status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
def create_user(request):
  """
  Create user for you organisation
  """
  serializer = UserSerializer(data=request.data)
  if serializer.is_valid():
    serializer.save(is_active=False, password= make_password(serializer.validated_data['password']))
    send_activate_email(request, serializer.validated_data["email"])

    return Response(serializer.data, status=status.HTTP_201_CREATED)
  return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', "DELETE", "PUT"])
@permission_classes([IsAuthenticated])
def get_user_detail(request, pk):
  """
  Access individual user data. If you are super user then you can
  access every user data. If you are active user then you can view or update only
  your own data.
  """
  try:
    user= User.objects.get(pk=pk)
  except:
    return Response({"details":"User does not exists"},status=status.HTTP_404_NOT_FOUND)
    
  if(request.user.is_superuser or request.user.id == pk):
    if request.method == "GET":
      serializer = UserSerializer(user)
      return Response(serializer.data, status = status.HTTP_200_OK)

    if request.method == "PUT":
      serializer = UserSerializer(user, data = request.data)
      if serializer.is_valid():
        serializer.save(password= make_password(serializer.validated_data['password']))
        return Response(serializer.data, status= status.HTTP_201_CREATED)
      return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)
  
    if request.method == "DELETE":
      user.delete()
      return Response(status=status.HTTP_204_NO_CONTENT)

  else :
    return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
def login_user(request):
  """
  Login Here to access you data or if you are a superuser
  then you can see all user data.
  """
  serializer = LoginSerializer(data=request.data,context={'request': request})
  if serializer.is_valid():
    try:
      user = User.objects.get(username=serializer.validated_data['username'])
    except:
      return Response({"error":"No user with this name"}, status=status.HTTP_404_NOT_FOUND)
    if(not user.check_password(serializer.validated_data['password']) or not user.is_authenticated):
      return Response({"error":"Unable to log in with provided credentials."},status=status.HTTP_400_BAD_REQUEST)
    login(request, user)
    return Response(serializer.data,status=status.HTTP_200_OK)
  return Response({"details":"Enter a valid data"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_user(request):
  """
  Logout user if user is logged in 
  """
  logout(request)
  return Response({"success":"Logout successfully"},status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password(request):
  """
  Change password with your old password and create new password.
  """
  serializer = ChangePasswordSerializer(data=request.data)
  if(serializer.is_valid()):
    try:
      user = User.objects.get(username=serializer.validated_data['username'])
    except:
      return Response({"details":"No user found"}, status=status.HTTP_404_NOT_FOUND)
    if(serializer.validated_data["new_password"] != serializer.validated_data["confirm_password"]):
      return Response({"details":"Confirm password not same"}, status=status.HTTP_400_BAD_REQUEST)
    if( not user.check_password(serializer.validated_data["old_password"])):
      return Response({"details":"Old assword incorrect"},status=status.HTTP_400_BAD_REQUEST)
    user.password = make_password(serializer.validated_data["new_password"])
    user.save()
  return Response({"success":"Password Changed Successfully"})


@api_view(["GET"])
def activate_account(request, uidb64, token):
  """
  Working of activate account 
  """
  uid = force_text(urlsafe_base64_decode(uidb64))
  try:
    user= User.objects.get(pk=uid)
  except:
    return Response({"error":"There is some issue to activate you account!!"}, status=status.HTTP_406_NOT_ACCEPTABLE)
  if user is not None and generate_token.check_token(user, token):
    user.is_active = True
    user.save()
    return Response({"success":"Your account has been activates successfully!","message":"Thanks for joining us!"}, status=status.HTTP_200_OK)
  else :
    return Response({"error":"There is some issue with the account!"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def reset_password(request):
  """
  If you forgot you account password then you easily create new password
  using your email address.
  """
  serializer = ResetPasswordSerializer(data = request.data)
  if serializer.is_valid():
    try:
      user = User.objects.get(email = serializer.validated_data["email"])
    except :
      return Response({"error":"No user found with this email address!"}, status=status.HTTP_404_NOT_FOUND)
    if user is not None:
      token = generate_token.make_token(user)
      uidb64 = str(urlsafe_base64_encode(force_bytes(user.id)))
      site = str(get_current_site(request))
      send_mail (
        subject="A new user found!!",
        message="Hii"+ user.username+", Hope you are doing well. To activate your account please check your mail and click on the link sent to you.\
        Confirmation Link : http://" + site +"/reset/"+uidb64+"/"+token,
        from_email="test@gmail.com",
        recipient_list=[user.email],
        fail_silently=True
      )
      return Response({"details":"Please check you email to reset your password!"})
  return Response({"error":"please enter a valid data!"})


@api_view(["POST"])
def create_password(request, uidb64, token):
  """
  Create a new password if you forgot your password.
  """
  serializer = ResetNewPasswordSerializer(data= request.data)
  if serializer.is_valid():
    uid = force_text(urlsafe_base64_decode(uidb64))
    try:
      user= User.objects.get(pk=uid)
    except:
      return Response({"error":"User not found!!"}, status=status.HTTP_404_NOT_FOUND)
    if user is not None and generate_token.check_token(user,token):
      if(serializer.validated_data["new_password"]!= serializer.validated_data["confirm_password"]):
        return Response({"error":"Confirm password not same as new password"},status=status.HTTP_400_BAD_REQUEST)
      user.password = make_password(serializer.validated_data["new_password"])
      user.save()
      return Response({"success":"Your password reset successfully!"}, status=status.HTTP_200_OK)
  return Response({"error":"Enter valid data!"}, status=status.HTTP_400_BAD_REQUEST)


def send_activate_email(req, email):
  """
  Send user an email to activate his account
  As well as user will click on the link it will activate its account.
  """
  try:
    user = User.objects.get(email= email)
  except:
    return
  token = generate_token.make_token(user)
  uidb64 = str(urlsafe_base64_encode(force_bytes(user.id)))
  site = str(get_current_site(req))
  send_mail(
    subject="A new user found!!",
    message="Hii"+ user.username+", Hope you are doing well. To activate your account please check your mail and click on the link sent to you. Confirmation Link : http://" + site +"/activate/"+uidb64+"/"+str(token)+"/",
    from_email="test@gmail.com",
    recipient_list=[email]
  )