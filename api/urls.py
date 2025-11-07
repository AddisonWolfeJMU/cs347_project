from django.urls import path
from .views import login_view, logout_view, user_view, register_view, update_user_view,delete_user_view

urlpatterns = [
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("user/", user_view, name="user"),
    path("register/", register_view, name="register"),
    path("user/update/", update_user_view, name="user_update"),
    path("user/delete/", delete_user_view, name="user_delete"),
]