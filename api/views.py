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
from .models import BucketList, MyTrips, Trip, Plan, BNB, Rating, Review
from django.conf import settings


### Helper function to build image URLs ###
def get_image_url(request, image_field):
    """Build absolute URL for an image field"""
    if not image_field:
        return None
    try:
        # Get the relative URL from the image field (e.g., /media/trip_images/photo.jpg)
        relative_url = image_field.url
        
        # Use Django's build_absolute_uri which handles host/port correctly
        # This should use the backend server's host (e.g., localhost:8000)
        absolute_url = request.build_absolute_uri(relative_url)
        
        # Debug: print the URL to help diagnose issues
        if settings.DEBUG:
            print(f"Image URL generated: {absolute_url} (from relative: {relative_url}, host: {request.get_host()})")
        
        return absolute_url
    except Exception as e:
        # Fallback: construct URL manually if build_absolute_uri fails
        print(f"Error in build_absolute_uri: {e}")
        try:
            if hasattr(image_field, 'name') and image_field.name:
                # Ensure MEDIA_URL starts with /
                media_url = settings.MEDIA_URL
                if not media_url.startswith('/'):
                    media_url = '/' + media_url
                # Ensure proper path joining
                if media_url.endswith('/') and image_field.name.startswith('/'):
                    image_path = media_url.rstrip('/') + image_field.name
                elif not media_url.endswith('/') and not image_field.name.startswith('/'):
                    image_path = media_url + '/' + image_field.name
                else:
                    image_path = media_url + image_field.name
                
                host = request.get_host()
                # Ensure port is included for backend server
                if ':' not in host and settings.DEBUG:
                    # Default to port 8000 for Django dev server
                    host = f"{host}:8000"
                scheme = request.scheme
                fallback_url = f"{scheme}://{host}{image_path}"
                if settings.DEBUG:
                    print(f"Fallback image URL: {fallback_url}")
                return fallback_url
        except Exception as fallback_error:
            print(f"Error building image URL (fallback): {fallback_error}")
            pass
        return None


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
            image_url = get_image_url(request, trip.image)
            
            trips_data.append({
                "id": trip.id,
                "name": trip.name,
                "location": trip.location,
                "date": trip.date.isoformat() if trip.date else None,
                "image": image_url,
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
            image_url = get_image_url(request, trip.image)
            
            trips_data.append({
                "id": trip.id,
                "name": trip.name,
                "location": trip.location,
                "date": trip.date.isoformat() if trip.date else None,
                "image": image_url,
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
        user = request.user
        
        # Handle both JSON and multipart/form-data
        if request.content_type and 'multipart/form-data' in request.content_type:
            name = request.POST.get("name")
            location = request.POST.get("location")
            date_str = request.POST.get("date")
            image = request.FILES.get("image")
        else:
            # Try JSON
            try:
                data = json.loads(request.body)
                name = data.get("name")
                location = data.get("location")
                date_str = data.get("date")
                image = None
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid request format."}, status=400)
        
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
            date=date,
            image=image if image else None
        )
        
        # Add to bucket list
        bucket_list, created = BucketList.objects.get_or_create(user=user)
        bucket_list.trips.add(trip)
        
        # Build image URL if image exists
        image_url = get_image_url(request, trip.image)
        
        return JsonResponse({
            "success": True,
            "trip": {
                "id": trip.id,
                "name": trip.name,
                "location": trip.location,
                "date": trip.date.isoformat() if trip.date else None,
                "image": image_url,
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
        user = request.user
        
        # Handle both JSON and multipart/form-data
        if request.content_type and 'multipart/form-data' in request.content_type:
            name = request.POST.get("name")
            location = request.POST.get("location")
            date_str = request.POST.get("date")
            image = request.FILES.get("image")
        else:
            # Try JSON
            try:
                data = json.loads(request.body)
                name = data.get("name")
                location = data.get("location")
                date_str = data.get("date")
                image = None
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid request format."}, status=400)
        
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
            date=date,
            image=image if image else None
        )
        
        # Add to MyTrips
        my_trips, created = MyTrips.objects.get_or_create(user=user)
        my_trips.trips.add(trip)
        
        # Build image URL if image exists
        image_url = get_image_url(request, trip.image)
        
        return JsonResponse({
            "success": True,
            "trip": {
                "id": trip.id,
                "name": trip.name,
                "location": trip.location,
                "date": trip.date.isoformat() if trip.date else None,
                "image": image_url,
            },
            "message": "Trip created and added to My Trips successfully."
        })
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


### Get Trip Details ###
@json_login_required
@csrf_exempt
def get_trip_view(request, trip_id):
    """Get detailed information about a specific trip"""
    user = request.user
    try:
        trip = Trip.objects.get(id=trip_id, user=user)
        
        # Check if trip is in MyTrips (completed) or just in BucketList (not completed)
        my_trips, _ = MyTrips.objects.get_or_create(user=user)
        is_completed = my_trips.trips.filter(id=trip_id).exists()
        
        # Get image URL
        image_url = get_image_url(request, trip.image)
        
        # Get plans
        plans = trip.plans.all()
        plans_data = [{
            "id": plan.id,
            "name": plan.name,
            "activity": plan.activity or "",
        } for plan in plans]
        
        # Get BNB if exists
        bnb_data = None
        try:
            bnb = trip.bnbs
            # Get ratings and reviews for this BNB (only if trip is completed)
            ratings = bnb.ratings.all()
            reviews = bnb.reviews.all()
            
            avg_rating = None
            if ratings.exists():
                avg_rating = sum(r.value for r in ratings) / ratings.count()
            
            ratings_data = [{"id": r.id, "value": r.value} for r in ratings]
            reviews_data = [{
                "id": rev.id,
                "statement": rev.statement,
                "rating_id": rev.rating.id if rev.rating else None,
            } for rev in reviews]
            
            bnb_data = {
                "id": bnb.id,
                "name": bnb.name,
                "address": bnb.address,
                "availability": bnb.availability,
                "average_rating": round(avg_rating, 1) if avg_rating else None,
                "ratings": ratings_data if is_completed else [],  # Only show ratings if completed
                "reviews": reviews_data if is_completed else [],  # Only show reviews if completed
            }
        except BNB.DoesNotExist:
            pass
        
        return JsonResponse({
            "success": True,
            "trip": {
                "id": trip.id,
                "name": trip.name,
                "location": trip.location,
                "date": trip.date.isoformat() if trip.date else None,
                "image": image_url,
                "plans": plans_data,
                "bnb": bnb_data,
                "is_completed": is_completed,  # Flag to indicate if trip is completed
            }
        })
    except Trip.DoesNotExist:
        return JsonResponse({"error": "Trip not found."}, status=404)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


### Create Plan for Trip ###
@json_login_required
@csrf_exempt
def create_plan_view(request, trip_id):
    """Create a plan/activity for a trip"""
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    try:
        user = request.user
        trip = Trip.objects.get(id=trip_id, user=user)
        
        data = json.loads(request.body)
        name = data.get("name", "")
        activity = data.get("activity", "")
        
        plan = Plan.objects.create(
            trip=trip,
            name=name,
            activity=activity
        )
        
        return JsonResponse({
            "success": True,
            "plan": {
                "id": plan.id,
                "name": plan.name,
                "activity": plan.activity or "",
            }
        })
    except Trip.DoesNotExist:
        return JsonResponse({"error": "Trip not found."}, status=404)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


### Delete Plan ###
@json_login_required
@csrf_exempt
def delete_plan_view(request, plan_id):
    """Delete a plan"""
    if request.method != "DELETE":
        return JsonResponse({"error": "DELETE request required."}, status=400)
    
    try:
        user = request.user
        plan = Plan.objects.get(id=plan_id, trip__user=user)
        plan.delete()
        
        return JsonResponse({
            "success": True,
            "message": "Plan deleted successfully."
        })
    except Plan.DoesNotExist:
        return JsonResponse({"error": "Plan not found."}, status=404)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


### Create BNB for Trip ###
@json_login_required
@csrf_exempt
def create_bnb_view(request, trip_id):
    """Create a BNB/accommodation for a trip"""
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    try:
        user = request.user
        trip = Trip.objects.get(id=trip_id, user=user)
        
        # Check if BNB already exists (OneToOne relationship)
        if hasattr(trip, 'bnbs'):
            return JsonResponse({"error": "BNB already exists for this trip."}, status=400)
        
        data = json.loads(request.body)
        name = data.get("name", "")
        address = data.get("address", "")
        availability = data.get("availability", True)
        
        bnb = BNB.objects.create(
            trip=trip,
            name=name,
            address=address,
            availability=availability
        )
        
        return JsonResponse({
            "success": True,
            "bnb": {
                "id": bnb.id,
                "name": bnb.name,
                "address": bnb.address,
                "availability": bnb.availability,
            }
        })
    except Trip.DoesNotExist:
        return JsonResponse({"error": "Trip not found."}, status=404)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


### Update BNB ###
@json_login_required
@csrf_exempt
def update_bnb_view(request, bnb_id):
    """Update a BNB"""
    if request.method not in ["PUT", "PATCH", "POST"]:
        return JsonResponse({"error": "PUT, PATCH, or POST request required."}, status=400)
    
    try:
        user = request.user
        bnb = BNB.objects.get(id=bnb_id, trip__user=user)
        
        data = json.loads(request.body)
        
        if "name" in data:
            bnb.name = data.get("name")
        if "address" in data:
            bnb.address = data.get("address")
        if "availability" in data:
            bnb.availability = data.get("availability")
        
        bnb.save()
        
        return JsonResponse({
            "success": True,
            "bnb": {
                "id": bnb.id,
                "name": bnb.name,
                "address": bnb.address,
                "availability": bnb.availability,
            }
        })
    except BNB.DoesNotExist:
        return JsonResponse({"error": "BNB not found."}, status=404)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


### Create Rating for BNB ###
@json_login_required
@csrf_exempt
def create_rating_view(request, bnb_id):
    """Create a rating for a BNB (only for completed trips)"""
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    try:
        user = request.user
        bnb = BNB.objects.get(id=bnb_id, trip__user=user)
        
        # Check if trip is in MyTrips (completed)
        my_trips, _ = MyTrips.objects.get_or_create(user=user)
        if not my_trips.trips.filter(id=bnb.trip.id).exists():
            return JsonResponse({"error": "Cannot rate BNB for trips that haven't been completed yet."}, status=403)
        
        data = json.loads(request.body)
        value = data.get("value")
        
        if not value or not (1 <= value <= 5):
            return JsonResponse({"error": "Rating must be between 1 and 5."}, status=400)
        
        rating = Rating.objects.create(
            bnb=bnb,
            value=value
        )
        
        return JsonResponse({
            "success": True,
            "rating": {
                "id": rating.id,
                "value": rating.value,
            }
        })
    except BNB.DoesNotExist:
        return JsonResponse({"error": "BNB not found."}, status=404)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


### Create Review for BNB ###
@json_login_required
@csrf_exempt
def create_review_view(request, bnb_id):
    """Create a review for a BNB (only for completed trips)"""
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    try:
        user = request.user
        bnb = BNB.objects.get(id=bnb_id, trip__user=user)
        
        # Check if trip is in MyTrips (completed)
        my_trips, _ = MyTrips.objects.get_or_create(user=user)
        if not my_trips.trips.filter(id=bnb.trip.id).exists():
            return JsonResponse({"error": "Cannot review BNB for trips that haven't been completed yet."}, status=403)
        
        data = json.loads(request.body)
        statement = data.get("statement", "")
        rating_id = data.get("rating_id")
        
        if not statement:
            return JsonResponse({"error": "Review statement is required."}, status=400)
        
        rating = None
        if rating_id:
            try:
                rating = Rating.objects.get(id=rating_id, bnb=bnb)
            except Rating.DoesNotExist:
                pass
        
        review = Review.objects.create(
            bnb=bnb,
            statement=statement,
            rating=rating
        )
        
        return JsonResponse({
            "success": True,
            "review": {
                "id": review.id,
                "statement": review.statement,
                "rating_id": review.rating.id if review.rating else None,
            }
        })
    except BNB.DoesNotExist:
        return JsonResponse({"error": "BNB not found."}, status=404)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


import requests
import pandas as pd
from rest_framework.decorators import api_view
from rest_framework.response import Response

from backend.ml.pipeline import predict_comfort
from backend.ml.weather_utils import geocode_city
@api_view(["POST"])
def comfort_by_city(request):
    try:
        city = request.data.get("city")
        start = request.data.get("start_date")
        end = request.data.get("end_date")

        if not city or not start or not end:
            return Response({"error": "Missing required fields"}, status=400)

        # -----------------------------
        # 1. Geocode City -> lat/lon
        # -----------------------------
        geo = geocode_city(city)
        if not geo:
            return Response({"error": "Geocoding failed"}, status=500)

        lat = float(geo["lat"])
        lon = float(geo["lon"])
        # -----------------------------
        # 2. Build Open-Meteo Forecast URL
        # -----------------------------
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,"
            "wind_speed_10m_max,cloudcover_mean"
            "&hourly=relativehumidity_2m"
            f"&start_date={start}&end_date={end}&timezone=auto"
        )

        api_resp = requests.get(url).json()

        if "daily" not in api_resp or "hourly" not in api_resp:
            return Response({"error": "Weather fetch failed", "raw": api_resp}, status=500)

        daily = api_resp["daily"]
        hourly = api_resp["hourly"]

        # -----------------------------
        # 3. Build hourly humidity DataFrame
        # -----------------------------
        hourly_df = pd.DataFrame({
            "time": pd.to_datetime(hourly["time"]),
            "humidity": hourly["relativehumidity_2m"],
        })

        results = []

        # -----------------------------
        # 4. Loop over days and extract features
        # -----------------------------
        for i, date in enumerate(daily["time"]):
            day = pd.to_datetime(date).date()

            # Get hourly humidity for that day
            mask = hourly_df["time"].dt.date == day
            day_values = hourly_df.loc[mask, "humidity"]

            # Safe fallback
            humidity_max = float(day_values.max()) if not day_values.empty else 50.0

            # Build feature row
            row = {
                "temp_min": daily["temperature_2m_min"][i],
                "temp_max": daily["temperature_2m_max"][i],
                "precipitation": daily["precipitation_sum"][i],
                "humidity_max": humidity_max,
                "wind_max": daily["wind_speed_10m_max"][i],
                "cloudcover": daily["cloudcover_mean"][i],
                "lat": lat,
                "lon": lon,
                "month": pd.to_datetime(date).month,
            }

            # -----------------------------
            # 5. Predict comfort index
            # -----------------------------
            score = predict_comfort(row)

            results.append({
                "date": date,
                "city": city,
                "comfort_score": float(score),
                **row,
            })

        # -----------------------------
        # 6. Return results
        # -----------------------------
        return Response({"results": results}, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
