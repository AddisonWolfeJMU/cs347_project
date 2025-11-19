from django.urls import path
from .views import (
    login_view, logout_view, user_view, register_view, update_user_view, 
    delete_user_view, check_auth_view, bucket_list_view, my_trips_view,
    create_trip_view, add_to_bucket_list_view, add_to_my_trips_view,
    create_trip_for_bucket_list_view, create_trip_for_my_trips_view,
    get_trip_view, create_plan_view, delete_plan_view, create_bnb_view,
    update_bnb_view, create_rating_view, create_review_view, comfort_by_city
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
    path("trips/<int:trip_id>/", get_trip_view, name="get_trip"),
    path("trips/<int:trip_id>/plans/", create_plan_view, name="create_plan"),
    path("plans/<int:plan_id>/", delete_plan_view, name="delete_plan"),
    path("trips/<int:trip_id>/bnb/", create_bnb_view, name="create_bnb"),
    path("bnb/<int:bnb_id>/", update_bnb_view, name="update_bnb"),
    path("bnb/<int:bnb_id>/ratings/", create_rating_view, name="create_rating"),
    path("bnb/<int:bnb_id>/reviews/", create_review_view, name="create_review"),
    path("comfort-by-city/", comfort_by_city),
]