<script>
  import { onMount } from 'svelte'
  import { getCurrentUser, logout, checkAuth, updateUser } from '../lib/api.js'
  import '../styles/general.css'
  
  let user = null
  let isLoading = true
  let error = ''
  let isLoggingOut = false
  let isEditing = false
  let isSaving = false
  let editForm = {
    username: '',
    first_name: '',
    last_name: '',
    email: ''
  }
  
  onMount(async () => {
    // Wait a bit to allow App.svelte's auth check to complete
    await new Promise(resolve => setTimeout(resolve, 100))
    await loadUserData()
  })
  
  async function loadUserData() {
    isLoading = true
    error = ''
    try {
      console.log('Profile: Loading user data...')
      // First try check-auth endpoint (doesn't require auth)
      const authCheck = await checkAuth()
      console.log('Profile: Auth check result:', authCheck)
      
      if (authCheck.is_authenticated) {
        user = {
          username: authCheck.username,
          id: authCheck.id,
          first_name: authCheck.first_name || '',
          last_name: authCheck.last_name || '',
          email: authCheck.email || ''
        }
        error = ''
        console.log('Profile: User data loaded from check-auth:', user)
      } else {
        // Try getCurrentUser as fallback (might give more info)
        try {
          const response = await getCurrentUser()
          if (response.is_authenticated) {
            user = {
              username: response.username,
              id: response.id,
              first_name: response.first_name || '',
              last_name: response.last_name || '',
              email: response.email || ''
            }
            error = ''
            console.log('Profile: User data loaded from getCurrentUser:', user)
          } else {
            console.log('Profile: Not authenticated, redirecting to login')
            // Wait a bit before redirecting to avoid flashing
            setTimeout(() => {
              window.location.hash = '#login'
            }, 500)
          }
        } catch (err) {
          console.log('Profile: getCurrentUser failed, redirecting to login')
          setTimeout(() => {
            window.location.hash = '#login'
          }, 500)
        }
      }
    } catch (err) {
      console.error('Profile: Failed to fetch user:', err)
      // Try one more time with a delay
      setTimeout(async () => {
        try {
          const authCheck = await checkAuth()
          if (authCheck.is_authenticated) {
            user = {
              username: authCheck.username,
              id: authCheck.id,
              first_name: authCheck.first_name || '',
              last_name: authCheck.last_name || '',
              email: authCheck.email || ''
            }
            error = ''
            isLoading = false
          } else {
            window.location.hash = '#login'
          }
        } catch (retryErr) {
          console.error('Profile: Retry failed, redirecting to login')
          window.location.hash = '#login'
        }
      }, 1000)
    } finally {
      isLoading = false
    }
  }
  
  function startEditing() {
    isEditing = true
    editForm = {
      username: user.username || '',
      first_name: user.first_name || '',
      last_name: user.last_name || '',
      email: user.email || ''
    }
    error = ''
  }
  
  function cancelEditing() {
    isEditing = false
    error = ''
  }
  
  async function saveChanges() {
    isSaving = true
    error = ''
    
    try {
      const response = await updateUser(editForm)
      
      if (response.success) {
        // Update user object with new data
        user = {
          ...user,
          username: response.username || user.username,
          first_name: response.first_name || '',
          last_name: response.last_name || '',
          email: response.email || ''
        }
        isEditing = false
      } else {
        error = response.error || 'Failed to update profile. Please try again.'
      }
    } catch (err) {
      console.error('Update error:', err)
      error = err.message || 'Failed to update profile. Please try again.'
    } finally {
      isSaving = false
    }
  }
  
  async function handleLogout() {
    isLoggingOut = true
    error = ''
    
    try {
      await logout()
      // Redirect to home page
      window.location.hash = '#home'
      window.location.reload() // Reload to update auth state
    } catch (err) {
      console.error('Logout error:', err)
      error = 'Logout failed. Please try again.'
      isLoggingOut = false
    }
  }
  
  function getDisplayName() {
    if (user.first_name || user.last_name) {
      return `${user.first_name || ''} ${user.last_name || ''}`.trim()
    }
    return user.username
  }
</script>

<main class="profile-page">
  <div class="container">
    {#if isLoading}
      <div class="loading-state">
        <div class="spinner"></div>
        <p>Loading profile...</p>
      </div>
    {:else if error && !user}
      <div class="error-state">
        <div class="alert alert-error">
          {error}
        </div>
        <button class="btn btn-primary" on:click={loadUserData}>
          Try Again
        </button>
      </div>
    {:else if user}
      <div class="profile-container">
        <div class="profile-header">
          <div class="profile-avatar">
            <span class="avatar-icon">{(user.first_name?.charAt(0) || user.username?.charAt(0) || 'U').toUpperCase()}</span>
          </div>
          <div class="profile-info">
            <h1>{getDisplayName()}</h1>
            <p class="user-subtitle">{user.username}</p>
            {#if user.email}
              <p class="user-email">{user.email}</p>
            {/if}
          </div>
        </div>
        
        {#if error}
          <div class="alert alert-error">
            {error}
          </div>
        {/if}
        
        <div class="profile-details">
          <div class="detail-card">
            <div class="card-header">
              <h3>Account Information</h3>
              {#if !isEditing}
                <button class="btn-edit" on:click={startEditing}>
                  <span>✏️</span> Edit
                </button>
              {/if}
            </div>
            
            {#if !isEditing}
              <div class="detail-list">
                <div class="detail-item">
                  <span class="detail-label">Username</span>
                  <span class="detail-value">{user.username}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">First Name</span>
                  <span class="detail-value">{user.first_name || 'Not set'}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">Last Name</span>
                  <span class="detail-value">{user.last_name || 'Not set'}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">Email</span>
                  <span class="detail-value">{user.email || 'Not set'}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">User ID</span>
                  <span class="detail-value">{user.id}</span>
                </div>
              </div>
            {:else}
              <form class="edit-form" on:submit|preventDefault={saveChanges}>
                <div class="form-group">
                  <label for="username">Username</label>
                  <input
                    id="username"
                    type="text"
                    bind:value={editForm.username}
                    placeholder="Username"
                    required
                  />
                </div>
                
                <div class="form-row">
                  <div class="form-group">
                    <label for="first_name">First Name</label>
                    <input
                      id="first_name"
                      type="text"
                      bind:value={editForm.first_name}
                      placeholder="First Name"
                    />
                  </div>
                  
                  <div class="form-group">
                    <label for="last_name">Last Name</label>
                    <input
                      id="last_name"
                      type="text"
                      bind:value={editForm.last_name}
                      placeholder="Last Name"
                    />
                  </div>
                </div>
                
                <div class="form-group">
                  <label for="email">Email</label>
                  <input
                    id="email"
                    type="email"
                    bind:value={editForm.email}
                    placeholder="email@example.com"
                  />
                </div>
                
                <div class="form-actions">
                  <button type="button" class="btn btn-secondary" on:click={cancelEditing} disabled={isSaving}>
                    Cancel
                  </button>
                  <button type="submit" class="btn btn-primary" disabled={isSaving}>
                    {#if isSaving}
                      Saving...
                    {:else}
                      Save Changes
                    {/if}
                  </button>
                </div>
              </form>
            {/if}
          </div>
        </div>
        
        <div class="profile-actions">
          <button 
            class="btn btn-danger" 
            on:click={handleLogout}
            disabled={isLoggingOut || isEditing}
          >
            {#if isLoggingOut}
              Logging out...
            {:else}
              Logout
            {/if}
          </button>
        </div>
      </div>
    {/if}
  </div>
</main>

<style>
  .profile-page {
    min-height: calc(100vh - 80px);
    padding: 2rem 1rem;
    background: #f7fafc;
  }
  
  .profile-container {
    max-width: 800px;
    margin: 0 auto;
  }
  
  .profile-header {
    background: white;
    border-radius: 16px;
    padding: 2.5rem;
    margin-bottom: 2rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    display: flex;
    align-items: center;
    gap: 2rem;
  }
  
  .profile-avatar {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }
  
  .avatar-icon {
    font-size: 3rem;
    font-weight: bold;
    color: white;
  }
  
  .profile-info h1 {
    font-size: 2rem;
    color: #1a202c;
    margin-bottom: 0.5rem;
  }
  
  .profile-info .user-subtitle {
    color: #718096;
    font-size: 1rem;
    margin: 0.25rem 0;
  }
  
  .profile-info .user-email {
    color: #4a5568;
    font-size: 0.9rem;
    margin: 0.25rem 0;
  }
  
  .profile-details {
    margin-bottom: 2rem;
  }
  
  .detail-card {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 0.75rem;
  }
  
  .detail-card h3 {
    font-size: 1.5rem;
    color: #1a202c;
    margin: 0;
  }
  
  .btn-edit {
    background: transparent;
    border: 2px solid #667eea;
    color: #667eea;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    font-size: 0.9rem;
    font-weight: 600;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.2s;
  }
  
  .btn-edit:hover {
    background: #667eea;
    color: white;
    transform: translateY(-1px);
  }
  
  .detail-list {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
  }
  
  .detail-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    background: #f7fafc;
    border-radius: 8px;
  }
  
  .detail-label {
    font-weight: 600;
    color: #4a5568;
  }
  
  .detail-value {
    color: #1a202c;
    font-weight: 500;
  }
  
  .edit-form {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
  }
  
  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
  }
  
  .form-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .form-group label {
    font-weight: 600;
    color: #4a5568;
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
  
  .form-group input:disabled {
    background-color: #f7fafc;
    cursor: not-allowed;
  }
  
  .form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    margin-top: 0.5rem;
  }
  
  .btn-secondary {
    background: #e2e8f0;
    color: #4a5568;
  }
  
  .btn-secondary:hover:not(:disabled) {
    background: #cbd5e0;
    transform: translateY(-1px);
  }
  
  .btn-secondary:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  .profile-actions {
    display: flex;
    justify-content: center;
    gap: 1rem;
  }
  
  .btn {
    padding: 0.875rem 2rem;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .btn-danger {
    background: #e53e3e;
    color: white;
  }
  
  .btn-danger:hover:not(:disabled) {
    background: #c53030;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(229, 62, 62, 0.4);
  }
  
  .btn-danger:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  .btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
  }
  
  .btn-primary:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  }
  
  .loading-state {
    text-align: center;
    padding: 4rem;
    color: #718096;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
  }
  
  .spinner {
    border: 4px solid #e2e8f0;
    border-top: 4px solid #667eea;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  .error-state {
    text-align: center;
    padding: 4rem;
    max-width: 500px;
    margin: 0 auto;
  }
  
  .alert {
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1.5rem;
    font-size: 0.9rem;
  }
  
  .alert-error {
    background-color: #fed7d7;
    color: #742a2a;
    border: 1px solid #fc8181;
  }
  
  @media (max-width: 640px) {
    .profile-header {
      flex-direction: column;
      text-align: center;
    }
    
    .detail-item {
      flex-direction: column;
      align-items: flex-start;
      gap: 0.5rem;
    }
    
    .form-row {
      grid-template-columns: 1fr;
    }
    
    .card-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 1rem;
    }
    
    .btn-edit {
      width: 100%;
      justify-content: center;
    }
  }
</style>

