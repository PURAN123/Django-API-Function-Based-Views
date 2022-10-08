from operator import truediv
from rest_framework.authtoken.models import Token
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from .models import User
from .serializer import ChangePasswordSerializer, LoginSerializer, ResetNewPasswordSerializer, ResetPasswordSerializer, UserSerializer
from django.contrib.auth import login, logout
from rest_auth.serializers import LoginSerializer
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_text
from django.contrib.sites.shortcuts import get_current_site

@api_view(["GET", "POST"])
# @permission_classes([IsAuthenticated])
def all_users(request):
  if(request.method == "GET"):
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
      return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_404_NOT_FOUND)

  if request.method == "POST" :
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save(is_active=False, password= make_password(serializer.validated_data['password']))
      user = User.objects.get(email= serializer.validated_data['email'])
      token = str(Token.objects.get(user=user))
      uidb64 = str(urlsafe_base64_encode(force_bytes(user.id)))
      site = str(get_current_site(request))
      send_mail(
        subject="A new user found!!",
        message="Hii"+ user.username+", Hope you are doing well. To activate your account please check your mail and click on the link sent to you.\
        Confirmation Link : http://" + site +"/activate/"+uidb64+"/"+token,
        from_email="test@gmail.com",
        recipient_list=[user.email],
        fail_silently=True
      )
      # activate_account(request._request, serializer.validated_data["email"])
      return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', "DELETE", "PUT"])
@permission_classes([IsAuthenticated])
def get_user_detail(request, pk):
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
  logout(request)
  return Response({"success":"Logout successfully"},status=status.HTTP_200_OK)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password(request):
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
  uid = force_text(urlsafe_base64_decode(uidb64))
  try:
    user= User.objects.get(pk=uid)
  except:
    return Response({"error":"There is some issue to activate you account!!"}, status=status.HTTP_406_NOT_ACCEPTABLE)
  if user is not None:
    user.is_active = True
    user.save()
    return Response({"success":"Your account has been activates successfully!","message":"Thanks for joining us!"}, status=status.HTTP_200_OK)
  else :
    return Response({"error":"There is some issue with the account!"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
def reset_password(request):
  serializer = ResetPasswordSerializer(data = request.data)
  if serializer.is_valid():
    try:
      user = User.objects.get(email = serializer.validated_data["email"])
    except :
      return Response({"error":"No user found with this email address!"}, status=status.HTTP_404_NOT_FOUND)
    if user is not None:
      token = str(Token.objects.get(user=user))
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
  serializer = ResetNewPasswordSerializer(data= request.data)
  if serializer.is_valid():
    uid = force_text(urlsafe_base64_decode(uidb64))
    try:
      user= User.objects.get(pk=uid)
    except:
      return Response({"error":"User not found!!"}, status=status.HTTP_404_NOT_FOUND)
    if user is not None:
      if(serializer.validated_data["new_password"]!= serializer.validated_data["confirm_password"]):
        return Response({"error":"Confirm password not same as new password"},status=status.HTTP_400_BAD_REQUEST)
      user.password = make_password(serializer.validated_data["new_password"])
      user.save()
      return Response({"success":"Your password reset successfully!"}, status=status.HTTP_200_OK)
  return Response({"error":"Anter valid data!"}, status=status.HTTP_400_BAD_REQUEST)



# def activate_account(req, email):
#   try:
#     user = User.objects.get(email= "pchandra1002@gmail.com")
#   except:
#     return
#   token = str(Token.objects.get(user=user))
#   uidb64 = str(urlsafe_base64_encode(force_bytes(user.id)))
#   site = str(get_current_site(req))
#   print(req)
#   send_mail(
#     subject="A new user found!!",
#     message="Hii"+ user.username+", Hope you are doing well. To activate your account please check your mail and click on the link sent to you. Confirmation Link : http://" + site +"/activate/"+uidb64+"/"+token+"/",
#     from_email="test@gmail.com",
#     recipient_list=[email]
#   )
