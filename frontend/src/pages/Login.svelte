<script>
  import { onMount } from 'svelte'
  import { login, checkAuth } from '../lib/api.js'
  import '../styles/general.css'
  
  let formData = {
    username: '',
    password: ''
  }
  
  let errors = {}
  let isLoading = false
  let successMessage = ''
  
  async function handleSubmit() {
    errors = {}
    successMessage = ''
    isLoading = true
    
    // Basic validation
    if (!formData.username) {
      errors.username = 'Username is required'
      isLoading = false
      return
    }
    if (!formData.password) {
      errors.password = 'Password is required'
      isLoading = false
      return
    }
    
    try {
      console.log('Login: Attempting login for:', formData.username)
      const response = await login(formData.username, formData.password)
      console.log('Login: Login response:', response)
      
      if (response.success) {
        console.log('Login: Login successful, session_key:', response.session_key)
        successMessage = 'Login successful! Redirecting...'
        
        // Check if we have the session cookie
        const cookies = document.cookie
        console.log('Login: Current cookies:', cookies)
        const hasSessionCookie = cookies.includes('sessionid')
        console.log('Login: Has session cookie:', hasSessionCookie)
        
        // Wait a moment for the session cookie to be set
        await new Promise(resolve => setTimeout(resolve, 500))
        
        // Check cookies again after delay
        const cookiesAfter = document.cookie
        console.log('Login: Cookies after delay:', cookiesAfter)
        const hasSessionCookieAfter = cookiesAfter.includes('sessionid')
        console.log('Login: Has session cookie after delay:', hasSessionCookieAfter)
        
        // Verify auth before redirecting
        try {
          const authCheck = await checkAuth()
          console.log('Login: Auth verification:', authCheck)
          console.log('Login: Has cookie in check:', authCheck.has_cookie)
          console.log('Login: Cookies received by backend:', authCheck.cookies_received)
          
          if (authCheck.is_authenticated) {
            // Store auth event to trigger update in App.svelte
            if (typeof window !== 'undefined') {
              localStorage.setItem('auth_update', Date.now().toString())
              // Dispatch a custom event to update auth state without reload
              window.dispatchEvent(new Event('auth-state-changed'))
            }
            
            // Redirect to profile page
            setTimeout(() => {
              window.location.hash = '#profile'
            }, 500)
          } else {
            // Session not verified - this means cookie wasn't set or sent
            console.error('Login: Session not verified after login!')
            console.error('Login: This usually means the cookie was not set or is being blocked')
            errors.general = 'Login successful but session not created. Please check browser settings or try again.'
            isLoading = false
          }
        } catch (verifyError) {
          console.error('Login: Auth verification failed:', verifyError)
          errors.general = 'Login successful but could not verify session. Please refresh the page.'
          isLoading = false
        }
      } else {
        errors.general = response.error || 'Login failed. Please try again.'
      }
    } catch (error) {
      console.error('Login error:', error)
      errors.general = error.message || 'Invalid username or password. Please try again.'
    } finally {
      isLoading = false
    }
  }
  
  function handleKeyPress(event) {
    if (event.key === 'Enter') {
      handleSubmit()
    }
  }
  
  // Check if already logged in
  onMount(async () => {
    try {
      const authStatus = await checkAuth()
      if (authStatus.is_authenticated) {
        window.location.hash = '#home'
        window.location.reload()
      }
    } catch (error) {
      // Ignore errors, just proceed with login form
    }
  })
</script>

<main class="auth-page">
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <h1>Welcome Back</h1>
        <p>Sign in to your PINPOINT account</p>
      </div>
      
      {#if successMessage}
        <div class="alert alert-success">
          {successMessage}
        </div>
      {/if}
      
      {#if errors.general}
        <div class="alert alert-error">
          {errors.general}
        </div>
      {/if}
      
      <form on:submit|preventDefault={handleSubmit} class="auth-form">
        <div class="form-group">
          <label for="username">Username</label>
          <input
            id="username"
            type="text"
            bind:value={formData.username}
            placeholder="Enter your username"
            class:error={errors.username}
            disabled={isLoading}
            on:keypress={handleKeyPress}
          />
          {#if errors.username}
            <span class="error-message">{errors.username}</span>
          {/if}
        </div>
        
        <div class="form-group">
          <label for="password">Password</label>
          <input
            id="password"
            type="password"
            bind:value={formData.password}
            placeholder="Enter your password"
            class:error={errors.password}
            disabled={isLoading}
            on:keypress={handleKeyPress}
          />
          {#if errors.password}
            <span class="error-message">{errors.password}</span>
          {/if}
        </div>
        
        <button type="submit" class="btn btn-primary" disabled={isLoading}>
          {#if isLoading}
            Signing In...
          {:else}
            Sign In
          {/if}
        </button>
      </form>
      
      <div class="auth-footer">
        <p>Don't have an account? <a href="#register">Sign up</a></p>
      </div>
    </div>
  </div>
</main>

<style>
  .auth-page {
    min-height: calc(100vh - 80px);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem 1rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }
  
  .auth-container {
    width: 100%;
    max-width: 450px;
  }
  
  .auth-card {
    background: white;
    border-radius: 16px;
    padding: 2.5rem;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  }
  
  .auth-header {
    text-align: center;
    margin-bottom: 2rem;
  }
  
  .auth-header h1 {
    font-size: 2rem;
    color: #1a202c;
    margin-bottom: 0.5rem;
  }
  
  .auth-header p {
    color: #718096;
    font-size: 0.95rem;
  }
  
  .auth-form {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
  }
  
  .form-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .form-group label {
    font-weight: 600;
    color: #2d3748;
    font-size: 0.9rem;
  }
  
  .form-group input {
    padding: 0.75rem;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    font-size: 1rem;
    transition: border-color 0.2s;
  }
  
  .form-group input:focus {
    outline: none;
    border-color: #667eea;
  }
  
  .form-group input.error {
    border-color: #e53e3e;
  }
  
  .form-group input:disabled {
    background-color: #f7fafc;
    cursor: not-allowed;
  }
  
  .error-message {
    color: #e53e3e;
    font-size: 0.85rem;
  }
  
  .btn {
    padding: 0.875rem 1.5rem;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
  }
  
  .btn-primary:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
  }
  
  .btn-primary:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  .auth-footer {
    margin-top: 1.5rem;
    text-align: center;
  }
  
  .auth-footer p {
    color: #718096;
    font-size: 0.9rem;
  }
  
  .auth-footer a {
    color: #667eea;
    text-decoration: none;
    font-weight: 600;
  }
  
  .auth-footer a:hover {
    text-decoration: underline;
  }
  
  .alert {
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1.5rem;
    font-size: 0.9rem;
  }
  
  .alert-success {
    background-color: #c6f6d5;
    color: #22543d;
    border: 1px solid #9ae6b4;
  }
  
  .alert-error {
    background-color: #fed7d7;
    color: #742a2a;
    border: 1px solid #fc8181;
  }
</style>
