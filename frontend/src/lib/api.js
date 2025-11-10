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
