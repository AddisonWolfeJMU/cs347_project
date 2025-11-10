<script>
  import { onMount } from 'svelte'
  import { register, checkAuth } from '../lib/api.js'
  import '../styles/general.css'
  
  let formData = {
    username: '',
    password: '',
    password_confirm: ''
  }
  
  let errors = {}
  let isLoading = false
  let successMessage = ''
  
  async function handleSubmit() {
    errors = {}
    successMessage = ''
    isLoading = true
    
    // Basic validation
    if (!formData.username || formData.username.length < 3) {
      errors.username = 'Username must be at least 3 characters'
    }
    if (!formData.password || formData.password.length < 8) {
      errors.password = 'Password must be at least 8 characters'
    }
    if (formData.password !== formData.password_confirm) {
      errors.password_confirm = 'Passwords do not match'
    }
    
    if (Object.keys(errors).length > 0) {
      isLoading = false
      return
    }
    
    try {
      const response = await register(formData.username, formData.password)
      
      if (response.success) {
        successMessage = 'Registration successful! Redirecting...'
        
        // Verify the session was set by checking auth status
        // Wait a moment for the session cookie to be set
        await new Promise(resolve => setTimeout(resolve, 300))
        
        // Verify auth before redirecting
        try {
          const authCheck = await checkAuth()
          console.log('Register: Auth verification:', authCheck)
          
          if (authCheck.is_authenticated) {
            // Store auth event to trigger update in App.svelte
            if (typeof window !== 'undefined') {
              localStorage.setItem('auth_update', Date.now().toString())
              // Dispatch a custom event to update auth state without reload
              window.dispatchEvent(new Event('auth-state-changed'))
            }
            
            // Redirect to profile page (don't reload - let App.svelte handle auth check)
            setTimeout(() => {
              window.location.hash = '#profile'
            }, 500)
          } else {
            // Session might not be set yet, wait a bit more and reload
            console.warn('Register: Session not verified, reloading page')
            setTimeout(() => {
              window.location.hash = '#profile'
              window.location.reload()
            }, 1000)
          }
        } catch (verifyError) {
          console.error('Register: Auth verification failed:', verifyError)
          // Fallback: reload the page
          setTimeout(() => {
            window.location.hash = '#profile'
            window.location.reload()
          }, 1000)
        }
      } else {
        errors.general = response.error || 'Registration failed. Please try again.'
      }
    } catch (error) {
      console.error('Registration error:', error)
      errors.general = error.message || 'Registration failed. Please try again.'
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
      // Ignore errors, just proceed with registration form
    }
  })
</script>

<main class="auth-page">
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <h1>Create Account</h1>
        <p>Join PINPOINT and start planning your dream trips</p>
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
          <label for="username">Username *</label>
          <input
            id="username"
            type="text"
            bind:value={formData.username}
            placeholder="Choose a username"
            class:error={errors.username}
            disabled={isLoading}
            on:keypress={handleKeyPress}
          />
          {#if errors.username}
            <span class="error-message">{errors.username}</span>
          {/if}
        </div>
        
        <div class="form-group">
          <label for="password">Password *</label>
          <input
            id="password"
            type="password"
            bind:value={formData.password}
            placeholder="At least 8 characters"
            class:error={errors.password}
            disabled={isLoading}
            on:keypress={handleKeyPress}
          />
          {#if errors.password}
            <span class="error-message">{errors.password}</span>
          {/if}
        </div>
        
        <div class="form-group">
          <label for="password_confirm">Confirm Password *</label>
          <input
            id="password_confirm"
            type="password"
            bind:value={formData.password_confirm}
            placeholder="Confirm your password"
            class:error={errors.password_confirm}
            disabled={isLoading}
            on:keypress={handleKeyPress}
          />
          {#if errors.password_confirm}
            <span class="error-message">{errors.password_confirm}</span>
          {/if}
        </div>
        
        <button type="submit" class="btn btn-primary" disabled={isLoading}>
          {#if isLoading}
            Creating Account...
          {:else}
            Create Account
          {/if}
        </button>
      </form>
      
      <div class="auth-footer">
        <p>Already have an account? <a href="#login">Sign in</a></p>
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
    max-width: 500px;
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
  
  @media (max-width: 640px) {
    .auth-card {
      padding: 1.5rem;
    }
  }
</style>
