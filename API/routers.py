
from django.urls import path
from .classviewset import UserViewset, UserModelViewset
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register("users", UserViewset, basename="users")
router.register("all_users", UserModelViewset, basename="all_users" )

urlpatterns = router.urls
