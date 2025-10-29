<script>
  import Home from './pages/Home.svelte'
  import BucketList from './pages/BucketList.svelte'
  import MyTrips from './pages/MyTrips.svelte'
  import Profile from './pages/Profile.svelte'
  import Destination from './pages/Destination.svelte'
  import Help from './pages/Help.svelte'
  let query = ''
  let route = 'home'
  let isMenuOpen = false
  let isNavigatingForward = true
  
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
    // Replace with real navigation/search later
    alert(`Search for: ${query || 'anything'}`)
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
      </div>
    </nav>
  </div>
  <div class="accent"></div>
  
</header>

{#if route === 'home'}
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
{/if}
