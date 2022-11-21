
from django.urls import path, include
from .classviewset import UserViewset, UserModelViewset, UserGenericListView
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register("users", UserViewset, basename="users")
router.register("all_users", UserModelViewset, basename="all_users" )
urlpatterns = [
  path("", include(router.urls)),
  path("gen_users/", UserGenericListView.as_view({'get':'list'}), name= "gen_users"),
  
]


