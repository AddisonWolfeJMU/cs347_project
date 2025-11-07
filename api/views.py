from django.shortcuts import render
from django.contrib.auth import authenticate, login,logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods


### Delete a User ###
# Must be logged in
@login_required
@require_http_methods(["DELETE"])
@csrf_exempt  # remove later when CSRF is handled
def delete_user_view(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON."}, status=400)

    password = data.get("password")
    user = request.user

    # Require password confirmation
    if not password:
        return JsonResponse({"error": "Password is required to delete account."}, status=400)

    if not user.check_password(password):
        return JsonResponse({"error": "Incorrect password."}, status=403)

    # Delete user and log out
    username = user.username
    user.delete()
    logout(request)

    return JsonResponse({
        "success": True,
        "message": f"User '{username}' has been deleted successfully."
    })


### Update user info ###
# Only username for now since we dont have email auth
@login_required
@require_http_methods(["PUT", "PATCH"])
@csrf_exempt  # temporary until we set up CSRF properly
def update_user_view(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON."}, status=400)

    user = request.user

    # Only allow username update for now
    new_username = data.get("username")

    #require password to change username
    password = data.get("password")
    if not user.check_password(password):
        return JsonResponse({"error": "Incorrect password."}, status=403)
    
    if new_username:
        # prevent duplicate usernames
        if User.objects.filter(username=new_username).exclude(pk=user.pk).exists():
            return JsonResponse({"error": "Username already taken."}, status=400)
        user.username = new_username

    user.save()

    return JsonResponse({
        "success": True,
        "message": "User updated successfully.",
        "username": user.username,
    })


### Register New User ###
@csrf_exempt  # we'll remove this later once CSRF tokens are set up for Svelte
def register_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    try:
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({"error": "Invalid JSON format."}, status=400)

    # Validation checks
    if not username or not password:
        return JsonResponse({"error": "Username and password are required."}, status=400)
    if User.objects.filter(username=username).exists():
        return JsonResponse({"error": "Username already taken."}, status=400)

    # Create the user
    user = User.objects.create_user(username=username, password=password)

    return JsonResponse({
        "success": True,
        "message": "User registered successfully.",
        "user_id": user.id,
        "username": user.username,
    })


### User Login ###
@csrf_exempt  #change this later
def login_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    try:
        #get user data
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({"error": "Invalid JSON or missing fields."}, status=400)

    #get user
    user = authenticate(request, username=username, password=password)

    #success
    if user is not None:
        login(request, user)
        return JsonResponse({
            "success": True,
            "message": "Login successful",
            "username": user.username,
        })
    
    #invalid data
    else:
        return JsonResponse({
            "success": False,
            "error": "Invalid username or password"
        }, status=401)


### User Logout ###
@csrf_exempt  # remove later when CSRF is set up
def logout_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    logout(request)
    return JsonResponse({"success": True, "message": "Logged out successfully."})


### View User Data ###
@login_required
def user_view(request):
    user = request.user
    return JsonResponse({
        "is_authenticated": True,
        "username": user.username,
        "id": user.id,
    })
