<script>
  import '../styles/bucket-list.css'
  
  // Sample completed trips data - will be replaced with backend data later
  let allTrips = [
    {
      id: 1,
      title: "Visit the Northern Lights in Iceland",
      description: "Experience the magical aurora borealis in Iceland's winter landscape",
      category: "adventure",
      priority: "high",
      completed: false,
      dateAdded: "2024-01-15",
      image: "https://images.unsplash.com/photo-1531366936337-7c912a4589a7?w=400"
    },
    {
      id: 2,
      title: "Skydive in Dubai",
      description: "Jump from the world's highest skydiving location",
      category: "adventure",
      priority: "medium",
      completed: false,
      dateAdded: "2024-01-10",
      image: "https://images.unsplash.com/photo-1551524164-6cf2ac531c8b?w=400"
    },
    {
      id: 3,
      title: "Watch Sunrise at Machu Picchu",
      description: "Witness the ancient Incan city at dawn",
      category: "mountains",
      priority: "high",
      completed: false,
      dateAdded: "2024-01-08",
      image: "https://images.unsplash.com/photo-1526392060635-9d6019884377?w=400"
    },
    {
      id: 4,
      title: "Swim with Dolphins in Hawaii",
      description: "Experience the joy of swimming with these intelligent creatures",
      category: "beaches",
      priority: "medium",
      completed: true,
      dateAdded: "2023-12-20",
      completedDate: "2024-01-05",
      image: "https://images.unsplash.com/photo-1544551763-77ef2d0cfc6c?w=400"
    },
    {
      id: 5,
      title: "Explore the Streets of Tokyo",
      description: "Immerse yourself in the vibrant culture and cuisine of Tokyo",
      category: "cities",
      priority: "high",
      completed: true,
      dateAdded: "2024-01-12",
      completedDate: "2024-02-10",
      image: "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=400"
    },
    {
      id: 6,
      title: "Romantic Dinner in Paris",
      description: "Enjoy a candlelit dinner overlooking the Eiffel Tower",
      category: "romantic",
      priority: "medium",
      completed: true,
      dateAdded: "2024-01-05",
      completedDate: "2024-03-15",
      image: "https://images.unsplash.com/photo-1502602898536-47ad22581b52?w=400"
    },
    {
      id: 7,
      title: "Hike the Grand Canyon",
      description: "Conquer one of nature's greatest wonders",
      category: "adventure",
      priority: "high",
      completed: true,
      dateAdded: "2023-11-15",
      completedDate: "2024-04-20",
      image: "https://images.unsplash.com/photo-1547036967-23d11aacaee0?w=400"
    }
  ]
  
  // Filter to show only completed trips
  $: completedTrips = allTrips.filter(trip => trip.completed)
  
  let selectedFilter = 'all'
  let searchQuery = ''
  
  const categories = [
    { name: "All", emoji: "🌍", color: "#6366f1", value: "all" },
    { name: "Beaches", emoji: "🏖️", color: "#4FC3F7", value: "beaches" },
    { name: "Cities", emoji: "🏙️", color: "#FF7043", value: "cities" },
    { name: "Mountains", emoji: "🏔️", color: "#66BB6A", value: "mountains" },
    { name: "Adventure", emoji: "🧗‍♀️", color: "#AB47BC", value: "adventure" },
    { name: "Romantic", emoji: "💕", color: "#F06292", value: "romantic" }
  ]
  
  $: filteredTrips = completedTrips.filter(trip => {
    const matchesFilter = selectedFilter === 'all' || trip.category === selectedFilter
    const matchesSearch = trip.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         trip.description.toLowerCase().includes(searchQuery.toLowerCase())
    return matchesFilter && matchesSearch
  })
  
  $: sortedTrips = [...filteredTrips].sort((a, b) => {
    // Sort by completion date, most recent first
    return new Date(b.completedDate) - new Date(a.completedDate)
  })
  
  function getPriorityColor(priority) {
    switch (priority) {
      case 'high': return '#ef4444'
      case 'medium': return '#f59e0b'
      case 'low': return '#10b981'
      default: return '#6b7280'
    }
  }
  
  function getDaysSinceCompletion(completedDate) {
    const days = Math.floor((new Date() - new Date(completedDate)) / (1000 * 60 * 60 * 24))
    return days
  }
  
  function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    })
  }
  
  // Calculate total travel experiences
  $: totalCompleted = completedTrips.length
  $: categoryBreakdown = completedTrips.reduce((acc, trip) => {
    acc[trip.category] = (acc[trip.category] || 0) + 1
    return acc
  }, {})
</script>

<main class="bucket-list-page">
  <!-- Hero Section -->
  <section class="hero">
    <div class="container">
      <div class="hero-content">
        <h1>My Completed Trips</h1>
        <p>Celebrate your adventures and travel achievements</p>
        <div class="stats">
          <div class="stat-item">
            <span class="stat-number">{totalCompleted}</span>
            <span class="stat-label">Trips Completed</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">{Object.keys(categoryBreakdown).length}</span>
            <span class="stat-label">Categories</span>
          </div>
          
        </div>
      </div>
    </div>
  </section>

  <!-- Filters and Search -->
  <section class="filters-section">
    <div class="container">
      <div class="filters-header">
        <h2>Filter Your Adventures</h2>
        <div class="filters-controls">
          <div class="search-box">
            <input 
              type="text" 
              placeholder="Search your completed trips..." 
              bind:value={searchQuery}
              class="search-input"
            />
            <span class="search-icon">🔍</span>
          </div>
        </div>
      </div>
      
      <div class="category-filters">
        {#each categories as category}
          <button 
            class="category-btn {selectedFilter === category.value ? 'active' : ''}"
            style="--category-color: {category.color}"
            on:click={() => selectedFilter = category.value}
          >
            <span class="category-emoji">{category.emoji}</span>
            <span class="category-name">{category.name}</span>
            {#if categoryBreakdown[category.value]}
              <span class="category-count">({categoryBreakdown[category.value]})</span>
            {/if}
          </button>
        {/each}
      </div>
    </div>
  </section>

  <!-- Completed Trips -->
  <section class="bucket-items">
    <div class="container">
      {#if sortedTrips.length === 0}
        <div class="empty-state">
          <div class="empty-icon">✈️</div>
          <h3>No completed trips yet</h3>
          <p>Start your journey by adding items to your bucket list and completing your first adventure!</p>
        </div>
      {:else}
        <div class="items-grid">
          {#each sortedTrips as trip}
            <div class="bucket-item completed">
              <div class="item-image" style={`background-image: url('${trip.image}')`}>
                <div class="priority-badge" style={`background-color: ${getPriorityColor(trip.priority)}`}>
                  {trip.priority}
                </div>
                <div class="completed-badge">✓ Completed</div>
              </div>
              <div class="item-content">
                <div class="item-header">
                  <h3 class="item-title">{trip.title}</h3>
                  <span class="item-category">{trip.category}</span>
                </div>
                <p class="item-description">{trip.description}</p>
                <div class="item-footer">
                  <span class="item-date">Added: {formatDate(trip.dateAdded)}</span>
                  <span class="completed-date">✓ Completed: {formatDate(trip.completedDate)}</span>
                  <span class="days-ago">({getDaysSinceCompletion(trip.completedDate)} days ago)</span>
                </div>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  </section>

  <!-- Achievement CTA -->
  <section class="add-item-cta">
    <div class="container">
      <div class="cta-content">
        <h2>Keep the adventure going!</h2>
        <p>Your journey doesn't end here. Add more dreams to your bucket list and make them reality</p>
      </div>
    </div>
  </section>
</main>

<style>
  /* Override the lower opacity for completed items on My Trips page */
  .bucket-item.completed {
    opacity: 1 !important;
  }
  
  /* Remove the semi-transparent overlay that makes completed items look faded */
  .bucket-item.completed::before {
    display: none;
  }
  
  .completed-badge {
    position: absolute;
    top: 15px;
    left: 15px;
    padding: 8px 16px;
    background: rgba(16, 185, 129, 0.95);
    color: white;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
  }
  
  .days-ago {
    color: var(--muted);
    font-size: 0.85rem;
    font-style: italic;
  }
  
  .bucket-item.completed:hover .completed-badge {
    transform: scale(1.05);
    box-shadow: 0 6px 20px rgba(16, 185, 129, 0.6);
  }
  
  .category-count {
    font-size: 12px;
    opacity: 0.8;
    margin-left: 4px;
  }
  
  .category-btn.active .category-count {
    opacity: 1;
  }
</style>
