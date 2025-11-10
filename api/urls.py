from django.urls import path
from .views import (
    login_view, logout_view, user_view, register_view, update_user_view, 
    delete_user_view, check_auth_view, bucket_list_view, my_trips_view,
    create_trip_view, add_to_bucket_list_view, add_to_my_trips_view,
    create_trip_for_bucket_list_view, create_trip_for_my_trips_view
)

urlpatterns = [
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("user/", user_view, name="user"),
    path("register/", register_view, name="register"),
    path("check-auth/", check_auth_view, name="check_auth"),
    path("user/update/", update_user_view, name="user_update"),
    path("user/delete/", delete_user_view, name="user_delete"),
    path("bucket-list/", bucket_list_view, name="bucket_list"),
    path("my-trips/", my_trips_view, name="my_trips"),
    path("trips/create/", create_trip_view, name="create_trip"),
    path("trips/add-to-bucket-list/", add_to_bucket_list_view, name="add_to_bucket_list"),
    path("trips/add-to-my-trips/", add_to_my_trips_view, name="add_to_my_trips"),
    path("trips/create-for-bucket-list/", create_trip_for_bucket_list_view, name="create_trip_for_bucket_list"),
    path("trips/create-for-my-trips/", create_trip_for_my_trips_view, name="create_trip_for_my_trips"),
]