from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from .serializer import UserSerializer
from .models import User
from django.contrib.auth.hashers import make_password


class UserModelViewset(viewsets.ModelViewSet):
  queryset = User.objects.all()
  serializer_class= UserSerializer
  lookup_field = "id"



class UserViewset(viewsets.ViewSet):
  def list(self, request):
    queryset = User.objects.all()
    serializer = UserSerializer(queryset, many=True)
    return Response(serializer.data)

  def create(self, request):
    serializer = UserSerializer(data=request.data)
    if(serializer.is_valid()):
      serializer.save(password= make_password(serializer.validated_data['password']))
      return Response(serializer.data,status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  def retrieve(self, request, pk=None):
    try:
      queryset = User.objects.get(id = pk)
    except:
      return Response({"error":"User does not exists!"}, status=status.HTTP_404_NOT_FOUND)
    if queryset is not None:
      serializer = UserSerializer(queryset)
      return Response(serializer.data)

  def update(self, request, pk=None):
    try:
      queryset = User.objects.get(id = pk)
    except:
      return Response({"error":"User does not exists!"}, status=status.HTTP_404_NOT_FOUND)
    serializer = UserSerializer(queryset, data=request.data)
    if(serializer.is_valid()):
      serializer.save(password= make_password(serializer.validated_data['password']))
      return Response(serializer.data)
    return Response(serializer.errors)

  def partial_update(self, request, pk=None):
    try:
      queryset = User.objects.get(id = pk)
    except:
      return Response({"error":"User does not exists!"}, status= status.HTTP_404_NOT_FOUND)
    serializer = UserSerializer(queryset, data=request.data, partial=True)
    if(serializer.is_valid()):
      serializer.save()
      return Response(serializer.data)
    return Response(serializer.errors)

  def destroy(self, request, pk=None):
    try:
      queryset = User.objects.get(id = pk)
    except:
      return Response({"error":"User does not exists!"}, status= status.HTTP_404_NOT_FOUND)
    queryset.delete()
    return Response({"details":"user deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)

