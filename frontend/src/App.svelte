<script>
  import { onMount } from 'svelte'
  import Home from './pages/Home.svelte'
  import BucketList from './pages/BucketList.svelte'
  import MyTrips from './pages/MyTrips.svelte'
  import Profile from './pages/Profile.svelte'
  import Destination from './pages/Destination.svelte'
  import Help from './pages/Help.svelte'
  import Login from './pages/Login.svelte'
  import Register from './pages/Register.svelte'
  import { checkAuth } from './lib/api.js'
  
  let query = ''
  let route = 'home'
  let isMenuOpen = false
  let isNavigatingForward = true
  let user = null
  let isAuthenticated = false
  let isLoadingAuth = true
  
  function setRouteFromHash() {
    const hash = (location.hash || '#home').replace('#', '')
    let newRoute = ''
    
    if (hash.startsWith('destination/')) {
      newRoute = 'destination'
    } else {
      newRoute = hash || 'home'
    }
    
    route = newRoute
    isMenuOpen = false
    
    // Only scroll to top for forward navigation (not back button)
    if (isNavigatingForward && typeof window !== 'undefined') {
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
    
    // Reset the flag after handling the navigation
    isNavigatingForward = true
  }
  
  function handleNavigation(event) {
    isNavigatingForward = true
    setRouteFromHash()
  }
  if (typeof window !== 'undefined') {
    setRouteFromHash()
    
    // Listen for hash changes (includes back/forward button)
    window.addEventListener('hashchange', (event) => {
      // Check if this is a back/forward navigation
      const navigationType = performance.getEntriesByType('navigation')[0]?.type
      isNavigatingForward = navigationType !== 'back_forward'
      
      setRouteFromHash()
    })
    
    // Listen for popstate (back/forward button specifically)
    window.addEventListener('popstate', () => {
      isNavigatingForward = false
    })
  }
  function search() {
    // Trigger the filter in Home component by updating query
    // The Home component will automatically filter based on reactive statement
    query = query // This will trigger the reactive update in Home
  }
  
  // Check authentication status
  async function checkAuthStatus() {
    try {
      console.log('Checking auth status...')
      const response = await checkAuth()
      console.log('Auth check response:', response)
      isAuthenticated = response.is_authenticated || false
      if (response.is_authenticated) {
        user = {
          username: response.username,
          id: response.id
        }
        console.log('User authenticated:', user)
      } else {
        user = null
        console.log('User not authenticated')
      }
    } catch (error) {
      console.error('Auth check failed:', error)
      isAuthenticated = false
      user = null
    } finally {
      isLoadingAuth = false
      console.log('Auth check complete. isAuthenticated:', isAuthenticated)
    }
  }
  
  // Track last route to avoid unnecessary checks
  let lastRoute = ''
  
  // Check auth on mount - this ensures persistence across page refreshes
  onMount(() => {
    checkAuthStatus()
    lastRoute = route
    
    // Listen for storage events to update auth state when login happens
    if (typeof window !== 'undefined') {
      // Check for auth updates from login/register
      const checkAuthUpdate = () => {
        const authUpdate = localStorage.getItem('auth_update')
        if (authUpdate) {
          localStorage.removeItem('auth_update')
          checkAuthStatus()
        }
      }
      
      // Check immediately
      checkAuthUpdate()
      
      // Listen for storage changes (cross-tab updates)
      window.addEventListener('storage', (e) => {
        if (e.key === 'auth_update') {
          checkAuthStatus()
        }
      })
      
      // Listen for custom auth state change event
      window.addEventListener('auth-state-changed', () => {
        checkAuthStatus()
      })
      
      // Also check auth when window gains focus
      window.addEventListener('focus', () => {
        checkAuthStatus()
      })
      
      // Poll for auth updates (fallback) - but less frequently
      setInterval(checkAuthUpdate, 2000)
    }
  })
  
  // Check auth when navigating to auth-related pages to keep state in sync
  $: if (route && route !== lastRoute && !isLoadingAuth) {
    lastRoute = route
    // Always check auth when navigating to profile, login, or register pages
    if (route === 'login' || route === 'register' || route === 'profile') {
      checkAuthStatus()
    }
  }
  
  // Also check auth state periodically to catch any changes
  $: if (route === 'profile' && !isAuthenticated && !isLoadingAuth) {
    // If we're on profile but not authenticated, check again
    checkAuthStatus()
  }
  
</script>

<header class="topbar">
  <div class="container">
    <nav class="nav">
      <a class="brand" href="#home" on:click={handleNavigation}>PINPOINT</a>
      <button class="menu-btn" aria-label="Menu" aria-expanded={isMenuOpen} on:click={() => isMenuOpen = !isMenuOpen}>
        ☰
      </button>
      <div class="links {isMenuOpen ? 'open' : ''}">
        <a class="link {route==='home' ? 'active' : ''}" href="#home" on:click={handleNavigation}>
          <span class="nav-icon">🏠</span>
          <span class="nav-text">Home</span>
        </a>
        <a class="link {route==='bucket' ? 'active' : ''}" href="#bucket" on:click={handleNavigation}>
          <span class="nav-icon">📝</span>
          <span class="nav-text">Bucket List</span>
        </a>
        <a class="link {route==='trips' ? 'active' : ''}" href="#trips" on:click={handleNavigation}>
          <span class="nav-icon">✈️</span>
          <span class="nav-text">My Trips</span>
        </a>
        <a class="link {route==='profile' ? 'active' : ''}" href="#profile" on:click={handleNavigation}>
          <span class="nav-icon">👤</span>
          <span class="nav-text">Profile</span>
        </a>
        <a class="link {route==='help' ? 'active' : ""}" href="#help" on:click={handleNavigation}>
          <span class="nav-icon">❓</span>
          <span class="nav-text">Help</span>
        </a>
        {#if !isAuthenticated}
          <a class="link {route==='login' ? 'active' : ''}" href="#login" on:click={handleNavigation}>
            <span class="nav-icon">🔐</span>
            <span class="nav-text">Login</span>
          </a>
          <a class="link {route==='register' ? 'active' : ''}" href="#register" on:click={handleNavigation}>
            <span class="nav-icon">✏️</span>
            <span class="nav-text">Sign Up</span>
          </a>
        {/if}
      </div>
    </nav>
  </div>
  <div class="accent"></div>
  
</header>

{#if isLoadingAuth}
  <main class="container" style="text-align: center; padding: 4rem;">
    <p>Loading...</p>
  </main>
{:else if route === 'home'}
  <Home {query} {search} />
{:else if route === 'bucket'}
  <BucketList />
{:else if route === 'trips'}
  <MyTrips />
{:else if route === 'profile'}
  <Profile />
{:else if route === 'destination'}
  <Destination />
{:else if route === 'help'}
  <Help />
{:else if route === 'login'}
  <Login />
{:else if route === 'register'}
  <Register />
{/if}
