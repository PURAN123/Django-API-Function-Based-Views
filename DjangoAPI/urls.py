from django.contrib import admin
from django.urls import path, include
from API.views import api_root
urlpatterns = [
    path('admin/', admin.site.urls),
    path("",api_root, name=""),
    path("api/v1/", include('API.urls')),
    path('rest-auth/', include('rest_auth.urls')),
    path('api-auth/', include('rest_framework.urls')),
]
