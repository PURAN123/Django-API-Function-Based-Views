
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .serializer import UserSerializer
from .models import User

class UsersList(generics.ListAPIView):
  permission_classes = [IsAuthenticated]
  # queryset = User.objects.all()
  serializer_class = UserSerializer

  def get_queryset(self):
    if self.request.user.is_superuser:
      return User.objects.all()
    elif self.request.user.is_authenticated:
      return User.objects.get(id = self.request.user.id)

  # def get_serializer(self, *args, **kwargs):
  #   return UserSerializer

  def list(self, request, *args, **kwargs):
    query_set = self.get_queryset()
    serializer = UserSerializer(query_set, many=True)
    return Response(serializer.data)