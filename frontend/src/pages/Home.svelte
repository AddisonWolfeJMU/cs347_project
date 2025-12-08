<script>
  import logo from '../assets/PinpointLogo.png'
  import '../styles/home.css'
  import { onMount } from 'svelte'
  export let query = ''
  export let search
  const onEnter = (e) => { if (e.key === 'Enter') search?.() }


  let destinations = {}
  let isLoadingDestinations = false

  // Helper function to categorize destinations based on their characteristics
  function categorizeDestination(name, description, region) {
    const nameLower = name.toLowerCase()
    const descLower = (description || '').toLowerCase()
    
    // Romantic destinations
    if (nameLower.includes('paris') || descLower.includes('romance') || descLower.includes('romantic')) {
      return 'romantic'
    }
    
    // Beach/coastal destinations
    if (nameLower.includes('dubai') || nameLower.includes('hong kong') || 
        descLower.includes('beach') || descLower.includes('coast')) {
      return 'beaches'
    }
    
    // Adventure destinations
    if (descLower.includes('adventure') || descLower.includes('safari') || 
        descLower.includes('hiking') || nameLower.includes('tokyo')) {
      return 'adventure'
    }
    
    // Default to cities (all our destinations are city-based)
    return 'cities'
  }

  onMount(async () => {
  isLoadingDestinations = true
  try {
    const res = await fetch('/practice_results.json', { cache: 'no-store' })
    if (!res.ok) throw new Error(`Failed to fetch destinations: ${res.status}`)
    const payload = await res.json()
    const combined = payload.results || {}
    const items = []

    for (const region of Object.keys(combined)) {
      const list = combined[region] || []
      for (const it of list) {
        const name = it.title || it.name || ''
        if (!name) continue
        const id = name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '')
        const image = it.thumbnail || it.image || ''
        const price = it.flight_price ? `From ${it.flight_price}` :
                      (it.extracted_flight_price ? `From $${it.extracted_flight_price}` : 'From $0')
        const description = it.description || ''
        const category = categorizeDestination(name, description, region)
        items.push({ id, name, image, price, category, region, description })
      }
    }

    destinations = Object.fromEntries(items.map(d => [d.id, d]))
    filterDestinations()   
  } catch (err) {
    console.error('Error loading destinations:', err)
    destinations = {}
    filterDestinations()
  } finally {
    isLoadingDestinations = false
  }
})
  // Filter categories
  const categories = [
    { name: "All", emoji: "🌍", color: "#6366f1", value: "all" },
    { name: "Europe", emoji: "🇪🇺", color: "#FF9800", value: "europe" },
    { name: "Asia", emoji: "🌏", color: "#E91E63", value: "asia" },
    { name: "Cities", emoji: "🏙️", color: "#FF7043", value: "cities" },
    { name: "Beaches", emoji: "🏖️", color: "#4FC3F7", value: "beaches" },
    { name: "Adventure", emoji: "🧗‍♀️", color: "#AB47BC", value: "adventure" },
    { name: "Romantic", emoji: "💕", color: "#F06292", value: "romantic" }
  ]
  
  let selectedCategory = 'all'
  let filteredDestinations = Object.values(destinations)
  
  function handleCategoryClick(category) {
    selectedCategory = category.value
    filterDestinations()
  }
  
  function filterDestinations() {
    let results = Object.values(destinations)
    
    // Apply category/region filter
    if (selectedCategory !== 'all') {
      results = results.filter(dest => {
        // Check if it's a region filter
        if (selectedCategory === 'europe' || selectedCategory === 'asia') {
          return dest.region && dest.region.toLowerCase() === selectedCategory
        }
        // Otherwise check category
        return dest.category === selectedCategory
      })
    }
    
    // Apply search query filter
    if (query && query.trim() !== '') {
      const searchTerm = query.toLowerCase().trim()
      results = results.filter(dest => 
        dest.name.toLowerCase().includes(searchTerm) ||
        (dest.category && dest.category.toLowerCase().includes(searchTerm)) ||
        (dest.region && dest.region.toLowerCase().includes(searchTerm)) ||
        (dest.description && dest.description.toLowerCase().includes(searchTerm)) ||
        dest.id.toLowerCase().includes(searchTerm)
      )
    }
    
    filteredDestinations = results
  }
  
  function navigateToDestination(destinationId) {
    window.location.hash = `#destination/${destinationId}`
  }
  
  // Watch for changes in query to automatically filter
  $: if (query !== undefined) {
    filterDestinations()
  }
  
  // Initialize filtered destinations
  filterDestinations()
</script>

<main class="home">
  <section class="hero container">
    <img class="brand-logo" src={logo} alt="Pinpoint logo" />
    <div class="search">
      <input
        placeholder="Explore your Dream Vacation"
        bind:value={query}
        on:keydown={onEnter}
        aria-label="Search"
      />
      <button class="search-btn" on:click={search} aria-label="Search">🔍</button>
    </div>
  </section>

  <!-- Filter Section -->
  <section class="filters">
    <div class="container">
      <h2>Filter Destinations</h2>
      <div class="filter-buttons">
        {#each categories as category}
          <button 
            class="filter-btn {selectedCategory === category.value ? 'active' : ''}"
            style="--category-color: {category.color}"
            on:click={() => handleCategoryClick(category)}
          >
            <span class="filter-emoji">{category.emoji}</span>
            <span class="filter-name">{category.name}</span>
          </button>
        {/each}
      </div>
    </div>
  </section>

  <!-- Destinations Grid -->
  <section class="destinations">
    <div class="container">
      <h2>Explore Popular Destinations</h2>
    </div>
    {#if filteredDestinations.length > 0}
      <div class="destinations-grid">
        {#each filteredDestinations as destination}
          <div class="destination-card" on:click={() => navigateToDestination(destination.id)}>
            <div class="destination-image" style={`background-image: url('${destination.image}')`}></div>
            <div class="destination-content">
              <h3>{destination.name}</h3>
              <p class="destination-price">{destination.price}</p>
            </div>
          </div>
        {/each}
      </div>
    {:else}
      <div class="no-results">
        <p class="no-results-text">No destinations found matching your search.</p>
        <p class="no-results-subtext">Try adjusting your search or filter criteria.</p>
      </div>
    {/if}
  </section>
</main>

<!-- Styles are imported from ../styles/home.css -->