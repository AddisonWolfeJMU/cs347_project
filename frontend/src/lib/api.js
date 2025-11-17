// API configuration
// IMPORTANT: Make sure this matches your frontend origin format!
// If frontend is on localhost, use localhost. If on 127.0.0.1, use 127.0.0.1
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

/**
 * Make an API request with proper error handling
 */
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const config = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    credentials: 'include', // Important for session cookies
  };

  try {
    const response = await fetch(url, config);
    
    // Handle network errors
    if (!response) {
      throw new Error('Network error: Unable to reach the server. Make sure the Django server is running on http://127.0.0.1:8000');
    }
    
    // Check if response is JSON
    const contentType = response.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
      // Response is not JSON, likely HTML (redirect or error page)
      const text = await response.text();
      console.error('Non-JSON response received:', {
        status: response.status,
        statusText: response.statusText,
        url: url,
        contentType: contentType,
        preview: text.substring(0, 200)
      });
      
      if (!response.ok) {
        throw new Error(`Server returned non-JSON response (${response.status}): ${response.statusText}`);
      }
      throw new Error('Server returned non-JSON response. Check server configuration.');
    }
    
    // Parse JSON response
    const data = await response.json();
    
    if (!response.ok) {
      // Handle error responses
      throw new Error(data.error || data.message || `HTTP error! status: ${response.status}`);
    }
    
    return data;
  } catch (error) {
    // Enhance error messages for network issues
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      console.error('API request failed - Network error:', error);
      throw new Error('Network error: Unable to reach the server. Make sure the Django server is running on http://127.0.0.1:8000');
    }
    console.error('API request failed:', error);
    throw error;
  }
}

/**
 * Register a new user
 */
export async function register(username, password) {
  return apiRequest('/register/', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  });
}

/**
 * Login a user
 */
export async function login(username, password) {
  return apiRequest('/login/', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  });
}

/**
 * Logout the current user
 */
export async function logout() {
  return apiRequest('/logout/', {
    method: 'POST',
  });
}

/**
 * Get current authenticated user
 */
export async function getCurrentUser() {
  try {
    return await apiRequest('/user/');
  } catch (error) {
    // If 401/403, user is not authenticated
    return { is_authenticated: false };
  }
}

/**
 * Update user information
 */
export async function updateUser(userData) {
  return apiRequest('/user/update/', {
    method: 'PATCH',
    body: JSON.stringify(userData),
  });
}

/**
 * Check authentication status
 */
export async function checkAuth() {
  try {
    return await apiRequest('/check-auth/');
  } catch (error) {
    // If there's a network error or the endpoint fails, return not authenticated
    console.error('Auth check error:', error);
    return { is_authenticated: false };
  }
}

/**
 * Get bucket list trips
 */
export async function getBucketList() {
  try {
    return await apiRequest('/bucket-list/');
  } catch (error) {
    console.error('Error fetching bucket list:', error);
    throw error;
  }
}

/**
 * Get my trips
 */
export async function getMyTrips() {
  try {
    return await apiRequest('/my-trips/');
  } catch (error) {
    console.error('Error fetching my trips:', error);
    throw error;
  }
}

/**
 * Create a new trip
 */
export async function createTrip(tripData) {
  try {
    return await apiRequest('/trips/create/', {
      method: 'POST',
      body: JSON.stringify(tripData),
    });
  } catch (error) {
    console.error('Error creating trip:', error);
    throw error;
  }
}

/**
 * Add trip to bucket list
 */
export async function addTripToBucketList(tripId) {
  try {
    return await apiRequest('/trips/add-to-bucket-list/', {
      method: 'POST',
      body: JSON.stringify({ trip_id: tripId }),
    });
  } catch (error) {
    console.error('Error adding trip to bucket list:', error);
    throw error;
  }
}

/**
 * Add trip to My Trips
 */
export async function addTripToMyTrips(tripId) {
  try {
    return await apiRequest('/trips/add-to-my-trips/', {
      method: 'POST',
      body: JSON.stringify({ trip_id: tripId }),
    });
  } catch (error) {
    console.error('Error adding trip to my trips:', error);
    throw error;
  }
}

/**
 * Create trip and add to bucket list in one call
 */
export async function createTripForBucketList(tripData) {
  try {
    const url = `${API_BASE_URL}/trips/create-for-bucket-list/`;
    
    // If tripData has an image file, use FormData
    if (tripData.image instanceof File) {
      const formData = new FormData();
      formData.append('name', tripData.name);
      formData.append('location', tripData.location);
      if (tripData.date) {
        formData.append('date', tripData.date);
      }
      formData.append('image', tripData.image);
      
      const response = await fetch(url, {
        method: 'POST',
        body: formData,
        credentials: 'include',
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to create trip');
      }
      
      return await response.json();
    } else {
      // Use JSON for requests without images
      return await apiRequest('/trips/create-for-bucket-list/', {
        method: 'POST',
        body: JSON.stringify(tripData),
      });
    }
  } catch (error) {
    console.error('Error creating trip for bucket list:', error);
    throw error;
  }
}

/**
 * Create trip and add to My Trips in one call
 */
export async function createTripForMyTrips(tripData) {
  try {
    const url = `${API_BASE_URL}/trips/create-for-my-trips/`;
    
    // If tripData has an image file, use FormData
    if (tripData.image instanceof File) {
      const formData = new FormData();
      formData.append('name', tripData.name);
      formData.append('location', tripData.location);
      if (tripData.date) {
        formData.append('date', tripData.date);
      }
      formData.append('image', tripData.image);
      
      const response = await fetch(url, {
        method: 'POST',
        body: formData,
        credentials: 'include',
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to create trip');
      }
      
      return await response.json();
    } else {
      // Use JSON for requests without images
      return await apiRequest('/trips/create-for-my-trips/', {
        method: 'POST',
        body: JSON.stringify(tripData),
      });
    }
  } catch (error) {
    console.error('Error creating trip for my trips:', error);
    throw error;
  }
}

/**
 * Get trip details
 */
export async function getTrip(tripId) {
  try {
    return await apiRequest(`/trips/${tripId}/`);
  } catch (error) {
    console.error('Error fetching trip:', error);
    throw error;
  }
}

/**
 * Create a plan for a trip
 */
export async function createPlan(tripId, planData) {
  try {
    return await apiRequest(`/trips/${tripId}/plans/`, {
      method: 'POST',
      body: JSON.stringify(planData),
    });
  } catch (error) {
    console.error('Error creating plan:', error);
    throw error;
  }
}

/**
 * Delete a plan
 */
export async function deletePlan(planId) {
  try {
    return await apiRequest(`/plans/${planId}/`, {
      method: 'DELETE',
    });
  } catch (error) {
    console.error('Error deleting plan:', error);
    throw error;
  }
}

/**
 * Create a BNB for a trip
 */
export async function createBNB(tripId, bnbData) {
  try {
    return await apiRequest(`/trips/${tripId}/bnb/`, {
      method: 'POST',
      body: JSON.stringify(bnbData),
    });
  } catch (error) {
    console.error('Error creating BNB:', error);
    throw error;
  }
}

/**
 * Update a BNB
 */
export async function updateBNB(bnbId, bnbData) {
  try {
    return await apiRequest(`/bnb/${bnbId}/`, {
      method: 'PATCH',
      body: JSON.stringify(bnbData),
    });
  } catch (error) {
    console.error('Error updating BNB:', error);
    throw error;
  }
}

/**
 * Create a rating for a BNB
 */
export async function createRating(bnbId, value) {
  try {
    return await apiRequest(`/bnb/${bnbId}/ratings/`, {
      method: 'POST',
      body: JSON.stringify({ value }),
    });
  } catch (error) {
    console.error('Error creating rating:', error);
    throw error;
  }
}

/**
 * Create a review for a BNB
 */
export async function createReview(bnbId, reviewData) {
  try {
    return await apiRequest(`/bnb/${bnbId}/reviews/`, {
      method: 'POST',
      body: JSON.stringify(reviewData),
    });
  } catch (error) {
    console.error('Error creating review:', error);
    throw error;
  }
}
