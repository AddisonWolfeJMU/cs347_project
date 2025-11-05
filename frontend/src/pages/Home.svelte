<script>
  import logo from '../assets/PinpointLogo.png'
  import '../styles/home.css'
  export let query = ''
  export let search
  const onEnter = (e) => { if (e.key === 'Enter') search?.() }
  
  // All destinations data
  const destinations = {
    'new-england': {
      name: 'New England',
      image: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=500',
      price: 'From $299',
      category: 'mountains',
      id: 'new-england'
    },
    'aspen-colorado': {
      name: 'Aspen, Colorado',
      image: 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=500',
      price: 'From $450',
      category: 'mountains',
      id: 'aspen-colorado'
    },
    'vermont': {
      name: 'Vermont',
      image: 'https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=500',
      price: 'From $199',
      category: 'mountains',
      id: 'vermont'
    },
    'bali-indonesia': {
      name: 'Bali, Indonesia',
      image: 'https://images.unsplash.com/photo-1537953773345-d172ccf13cf1?w=500',
      price: 'From $599',
      category: 'beaches',
      id: 'bali-indonesia'
    },
    'santorini-greece': {
      name: 'Santorini, Greece',
      image: 'https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=500',
      price: 'From $799',
      category: 'beaches',
      id: 'santorini-greece'
    },
    'dubai-uae': {
      name: 'Dubai, UAE',
      image: 'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=500',
      price: 'From $699',
      category: 'cities',
      id: 'dubai-uae'
    },
    'swiss-alps': {
      name: 'Swiss Alps',
      image: 'https://s1.it.atcdn.net/wp-content/uploads/2015/11/shutterstock_279572969.jpg',
      price: 'From $899',
      category: 'mountains',
      id: 'swiss-alps'
    },
    'iceland': {
      name: 'Iceland',
      image: 'https://cdn.britannica.com/06/171306-050-C88DD752/Aurora-borealis-peninsula-Snaefellsnes-Iceland-March-2013.jpg',
      price: 'From $599',
      category: 'adventure',
      id: 'iceland'
    },
    'banff-canada': {
      name: 'Banff, Canada',
      image: 'https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=500',
      price: 'From $399',
      category: 'mountains',
      id: 'banff-canada'
    }
  }
  
  // Filter categories
  const categories = [
    { name: "All", emoji: "🌍", color: "#6366f1", value: "all" },
    { name: "Beaches", emoji: "🏖️", color: "#4FC3F7", value: "beaches" },
    { name: "Cities", emoji: "🏙️", color: "#FF7043", value: "cities" },
    { name: "Mountains", emoji: "🏔️", color: "#66BB6A", value: "mountains" },
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
    
    // Apply category filter
    if (selectedCategory !== 'all') {
      results = results.filter(dest => dest.category === selectedCategory)
    }
    
    // Apply search query filter
    if (query && query.trim() !== '') {
      const searchTerm = query.toLowerCase().trim()
      results = results.filter(dest => 
        dest.name.toLowerCase().includes(searchTerm) ||
        dest.category.toLowerCase().includes(searchTerm) ||
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