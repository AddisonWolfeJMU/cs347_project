from django.shortcuts import render
from django.contrib.auth import authenticate, login,logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from functools import wraps
from .models import BucketList, MyTrips, Trip


### Custom decorator for JSON API endpoints that require login ###
def json_login_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required", "is_authenticated": False}, status=401)
        return view_func(request, *args, **kwargs)
    return wrapped_view


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
@json_login_required
@csrf_exempt
def update_user_view(request):
    if request.method not in ["PUT", "PATCH", "POST"]:
        return JsonResponse({"error": "PUT, PATCH, or POST request required."}, status=400)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON."}, status=400)

    user = request.user
    updated_fields = []

    # Update username if provided
    new_username = data.get("username")
    if new_username and new_username != user.username:
        # Prevent duplicate usernames
        if User.objects.filter(username=new_username).exclude(pk=user.pk).exists():
            return JsonResponse({"error": "Username already taken."}, status=400)
        user.username = new_username
        updated_fields.append("username")

    # Update first_name if provided
    if "first_name" in data:
        user.first_name = data.get("first_name", "")
        updated_fields.append("first_name")

    # Update last_name if provided
    if "last_name" in data:
        user.last_name = data.get("last_name", "")
        updated_fields.append("last_name")

    # Update email if provided
    if "email" in data:
        new_email = data.get("email", "")
        # Basic email validation
        if new_email and "@" not in new_email:
            return JsonResponse({"error": "Invalid email format."}, status=400)
        user.email = new_email
        updated_fields.append("email")

    # Save if any fields were updated
    if updated_fields:
        user.save()
        return JsonResponse({
            "success": True,
            "message": "User updated successfully.",
            "username": user.username,
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "email": user.email or "",
            "updated_fields": updated_fields,
        })
    else:
        return JsonResponse({
            "success": True,
            "message": "No changes to update.",
            "username": user.username,
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "email": user.email or "",
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
    
    # Automatically log the user in after registration
    login(request, user)
    
    # Force session to be saved
    request.session.modified = True
    request.session.save()
    
    # Get session key
    session_key = request.session.session_key
    
    # Create response
    response = JsonResponse({
        "success": True,
        "message": "User registered successfully.",
        "user_id": user.id,
        "username": user.username,
        "session_key": session_key,
    })
    
    # Manually set the session cookie (same as login)
    from django.conf import settings
    if session_key:
        cookie_value = session_key
        max_age = settings.SESSION_COOKIE_AGE
        
        # Set cookie with explicit attributes
        response.set_cookie(
            'sessionid',
            cookie_value,
            max_age=max_age,  # Use max_age (in seconds)
            path=settings.SESSION_COOKIE_PATH,
            domain=settings.SESSION_COOKIE_DOMAIN,
            secure=settings.SESSION_COOKIE_SECURE,
            httponly=settings.SESSION_COOKIE_HTTPONLY,
            samesite=settings.SESSION_COOKIE_SAMESITE
        )
    
    return response


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
        # Login the user (Django's login() creates/updates session)
        login(request, user)
        
        # Force session to be saved immediately
        request.session.modified = True
        request.session.save()
        
        # Get session key
        session_key = request.session.session_key
        print(f"Login: Session created - Key: {session_key}, User: {user.username}")
        
        # Create response
        response = JsonResponse({
            "success": True,
            "message": "Login successful",
            "username": user.username,
            "user_id": user.id,
            "session_key": session_key,
        })
        
        # Manually set the session cookie in the response
        # This ensures the cookie is definitely set, bypassing any middleware issues
        from django.conf import settings
        if session_key:
            cookie_value = session_key
            max_age = settings.SESSION_COOKIE_AGE
            
            # Set cookie with explicit attributes
            # Note: Use max_age OR expires, not both
            response.set_cookie(
                'sessionid',
                cookie_value,
                max_age=max_age,  # Use max_age (in seconds)
                path=settings.SESSION_COOKIE_PATH,
                domain=settings.SESSION_COOKIE_DOMAIN,
                secure=settings.SESSION_COOKIE_SECURE,
                httponly=settings.SESSION_COOKIE_HTTPONLY,
                samesite=settings.SESSION_COOKIE_SAMESITE
            )
            print(f"Login: Manually set session cookie: {cookie_value[:20]}...")
        
        return response
    
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


### Check Authentication Status ###
@csrf_exempt  # Allow GET requests without CSRF
def check_auth_view(request):
    """Check if user is authenticated (no login required)"""
    # Debug: Check if session exists
    has_session = request.session.session_key is not None
    session_key = request.session.session_key
    
    # Debug: Check cookies in request
    cookies = request.COOKIES
    has_session_cookie = 'sessionid' in cookies
    
    # Debug: Check origin
    origin = request.headers.get("Origin", "No Origin header")
    
    print(f"Check Auth: has_session={has_session}, session_key={session_key}, has_cookie={has_session_cookie}, origin={origin}")
    
    if request.user.is_authenticated:
        # Ensure session is saved
        if not request.session.modified:
            request.session.modified = True
        user = request.user
        response = JsonResponse({
            "is_authenticated": True,
            "username": user.username,
            "id": user.id,
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "email": user.email or "",
            "session_key": session_key if has_session else None,
            "has_cookie": has_session_cookie,
        })
        # Don't set CORS headers manually - middleware handles it
        return response
    else:
        response = JsonResponse({
            "is_authenticated": False,
            "has_session": has_session,
            "session_key": session_key if has_session else None,
            "has_cookie": has_session_cookie,
            "cookies_received": list(cookies.keys()),
            "origin": origin,
        })
        # Don't set CORS headers manually - middleware handles it
        return response


### View User Data ###
@json_login_required
@csrf_exempt
def user_view(request):
    user = request.user
    return JsonResponse({
        "is_authenticated": True,
        "username": user.username,
        "id": user.id,
        "first_name": user.first_name or "",
        "last_name": user.last_name or "",
        "email": user.email or "",
    })


### Get Bucket List ###
@json_login_required
@csrf_exempt
def bucket_list_view(request):
    """Get all trips in the user's bucket list"""
    user = request.user
    try:
        bucket_list, created = BucketList.objects.get_or_create(user=user)
        trips = bucket_list.trips.all()
        
        trips_data = []
        for trip in trips:
            trips_data.append({
                "id": trip.id,
                "name": trip.name,
                "location": trip.location,
                "date": trip.date.isoformat() if trip.date else None,
            })
        
        return JsonResponse({
            "success": True,
            "trips": trips_data,
        })
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


### Get My Trips ###
@json_login_required
@csrf_exempt
def my_trips_view(request):
    """Get all trips in the user's MyTrips"""
    user = request.user
    try:
        my_trips, created = MyTrips.objects.get_or_create(user=user)
        trips = my_trips.trips.all()
        
        trips_data = []
        for trip in trips:
            trips_data.append({
                "id": trip.id,
                "name": trip.name,
                "location": trip.location,
                "date": trip.date.isoformat() if trip.date else None,
            })
        
        return JsonResponse({
            "success": True,
            "trips": trips_data,
        })
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


### Create Trip ###
@json_login_required
@csrf_exempt
def create_trip_view(request):
    """Create a new trip"""
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    try:
        data = json.loads(request.body)
        user = request.user
        
        name = data.get("name")
        location = data.get("location")
        date_str = data.get("date")
        
        # Validation
        if not name or not location:
            return JsonResponse({"error": "Name and location are required."}, status=400)
        
        # Parse date if provided
        date = None
        if date_str:
            from datetime import datetime
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return JsonResponse({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)
        
        # Create trip
        trip = Trip.objects.create(
            user=user,
            name=name,
            location=location,
            date=date
        )
        
        return JsonResponse({
            "success": True,
            "trip": {
                "id": trip.id,
                "name": trip.name,
                "location": trip.location,
                "date": trip.date.isoformat() if trip.date else None,
            }
        })
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


### Add Trip to Bucket List ###
@json_login_required
@csrf_exempt
def add_to_bucket_list_view(request):
    """Add a trip to the user's bucket list"""
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    try:
        data = json.loads(request.body)
        user = request.user
        
        trip_id = data.get("trip_id")
        if not trip_id:
            return JsonResponse({"error": "trip_id is required."}, status=400)
        
        try:
            trip = Trip.objects.get(id=trip_id)
        except Trip.DoesNotExist:
            return JsonResponse({"error": "Trip not found."}, status=404)
        
        bucket_list, created = BucketList.objects.get_or_create(user=user)
        bucket_list.trips.add(trip)
        
        return JsonResponse({
            "success": True,
            "message": "Trip added to bucket list successfully."
        })
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


### Add Trip to My Trips ###
@json_login_required
@csrf_exempt
def add_to_my_trips_view(request):
    """Add a trip to the user's MyTrips"""
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    try:
        data = json.loads(request.body)
        user = request.user
        
        trip_id = data.get("trip_id")
        if not trip_id:
            return JsonResponse({"error": "trip_id is required."}, status=400)
        
        try:
            trip = Trip.objects.get(id=trip_id)
        except Trip.DoesNotExist:
            return JsonResponse({"error": "Trip not found."}, status=404)
        
        my_trips, created = MyTrips.objects.get_or_create(user=user)
        my_trips.trips.add(trip)
        
        return JsonResponse({
            "success": True,
            "message": "Trip added to My Trips successfully."
        })
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


### Create Trip and Add to Bucket List ###
@json_login_required
@csrf_exempt
def create_trip_for_bucket_list_view(request):
    """Create a new trip and add it to bucket list in one call"""
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    try:
        data = json.loads(request.body)
        user = request.user
        
        name = data.get("name")
        location = data.get("location")
        date_str = data.get("date")
        
        # Validation
        if not name or not location:
            return JsonResponse({"error": "Name and location are required."}, status=400)
        
        # Parse date if provided
        date = None
        if date_str:
            from datetime import datetime
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return JsonResponse({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)
        
        # Create trip
        trip = Trip.objects.create(
            user=user,
            name=name,
            location=location,
            date=date
        )
        
        # Add to bucket list
        bucket_list, created = BucketList.objects.get_or_create(user=user)
        bucket_list.trips.add(trip)
        
        return JsonResponse({
            "success": True,
            "trip": {
                "id": trip.id,
                "name": trip.name,
                "location": trip.location,
                "date": trip.date.isoformat() if trip.date else None,
            },
            "message": "Trip created and added to bucket list successfully."
        })
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


### Create Trip and Add to My Trips ###
@json_login_required
@csrf_exempt
def create_trip_for_my_trips_view(request):
    """Create a new trip and add it to MyTrips in one call"""
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    try:
        data = json.loads(request.body)
        user = request.user
        
        name = data.get("name")
        location = data.get("location")
        date_str = data.get("date")
        
        # Validation
        if not name or not location:
            return JsonResponse({"error": "Name and location are required."}, status=400)
        
        # Parse date if provided
        date = None
        if date_str:
            from datetime import datetime
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return JsonResponse({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)
        
        # Create trip
        trip = Trip.objects.create(
            user=user,
            name=name,
            location=location,
            date=date
        )
        
        # Add to MyTrips
        my_trips, created = MyTrips.objects.get_or_create(user=user)
        my_trips.trips.add(trip)
        
        return JsonResponse({
            "success": True,
            "trip": {
                "id": trip.id,
                "name": trip.name,
                "location": trip.location,
                "date": trip.date.isoformat() if trip.date else None,
            },
            "message": "Trip created and added to My Trips successfully."
        })
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)
