from os import stat
from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from .models import User
from .serializer import ChangePasswordSerializer, LoginSerializer, UserSerializer
from django.contrib.auth import login, logout
from rest_auth.serializers import LoginSerializer

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
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

  if not request.user.is_authenticated:
    if request.method == "POST" :
      serializer = UserSerializer(data=request.data)
      if serializer.is_valid():
        serializer.save(is_active=False, password= make_password(serializer.validated_data['password']))
        return Response(serializer.data, status=status.HTTP_201_CREATED)
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  else :
    return Response({"detail": "Can't Add another user."}, status=status.HTTP_400_BAD_REQUEST)



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
  serializer = LoginSerializer(data=request.data)
  if serializer.is_valid():
    print("pass")
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
