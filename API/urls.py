from django.urls import path
from .views import all_users, get_user_detail, login_user, logout_user, change_password, activate_account, reset_password, create_password
urlpatterns = [
    path("", all_users, name= "all_users" ),
    path("<int:pk>/",get_user_detail, name="details"),
    path("login/", login_user, name= "login"),
    path("logout/", logout_user, name= "logout"),
    path("change_password/",change_password, name="change_password"),
    path("reset_password/",reset_password, name="reset_password"),
    path("activate/<uidb64>/<token>/",activate_account, name="activate_account"),
    path("reset/<uidb64>/<token>/",create_password, name="reset_account"),
]
