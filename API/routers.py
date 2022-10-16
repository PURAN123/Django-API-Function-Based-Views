from rest_framework.routers import DefaultRouter
from .viewsClass import UserViewset
router = DefaultRouter()

router.register("users", UserViewset, basename = "users")
urlpatterns = router.urls
