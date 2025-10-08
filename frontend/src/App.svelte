<script>
  import Home from './pages/Home.svelte'
  import BucketList from './pages/BucketList.svelte'
  import MyTrips from './pages/MyTrips.svelte'
  import Profile from './pages/Profile.svelte'
  let query = ''
  let route = 'home'
  let isMenuOpen = false
  function setRouteFromHash() {
    const hash = (location.hash || '#home').replace('#', '')
    route = hash || 'home'
    isMenuOpen = false
  }
  if (typeof window !== 'undefined') {
    setRouteFromHash()
    window.addEventListener('hashchange', setRouteFromHash)
  }
  function search() {
    // Replace with real navigation/search later
    alert(`Search for: ${query || 'anything'}`)
  }
  const popular = [
    {
      title: 'Punta Cana',
      image: 'https://www.travelcenter.uk/blog/wp-content/uploads/2020/07/Punta-Cana.jpg',
    },
    {
      title: 'Italy',
      image: 'https://cdn.britannica.com/82/195482-050-2373E635/Amalfi-Italy.jpg',
    },
    {
      title: 'Paris',
      image: 'https://worldinparis.com/wp-content/uploads/2022/01/View-from-the-Pantheon.jpg',
    },
    {
      title: 'Tokyo',
      image: 'https://res.cloudinary.com/aenetworks/image/upload/c_fill,ar_2,w_3840,h_1920,g_auto/dpr_auto/f_auto/q_auto:eco/v1/gettyimages-1390815938?_a=BAVAZGID0',
    },
  ]
</script>

<header class="topbar">
  <div class="container">
    <nav class="nav">
      <a class="brand" href="#home">PINPOINT</a>
      <button class="menu-btn" aria-label="Menu" aria-expanded={isMenuOpen} on:click={() => isMenuOpen = !isMenuOpen}>
        ☰
      </button>
      <div class="links {isMenuOpen ? 'open' : ''}">
        <a class="link {route==='home' ? 'active' : ''}" href="#home" on:click={() => isMenuOpen = false}>HOME</a>
        <a class="link {route==='bucket' ? 'active' : ''}" href="#bucket" on:click={() => isMenuOpen = false}>BUCKET LIST</a>
        <a class="link {route==='trips' ? 'active' : ''}" href="#trips" on:click={() => isMenuOpen = false}>MY TRIPS</a>
        <a class="link {route==='profile' ? 'active' : ''}" href="#profile" on:click={() => isMenuOpen = false}>PROFILE</a>
      </div>
    </nav>
  </div>
  <div class="accent"></div>
  
</header>

{#if route === 'home'}
<Home {query} {popular} {search} />
{:else if route === 'bucket'}
<BucketList />
{:else if route === 'trips'}
<MyTrips />
{:else if route === 'profile'}
<Profile />
{/if}
