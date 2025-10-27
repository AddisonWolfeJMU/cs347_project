<script>
  import '../styles/bucket-list.css'
  
  // Sample bucket list data - will be replaced with backend data later
  let bucketListItems = [
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
      completed: false,
      dateAdded: "2024-01-12",
      image: "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=400"
    },
    {
      id: 6,
      title: "Romantic Dinner in Paris",
      description: "Enjoy a candlelit dinner overlooking the Eiffel Tower",
      category: "romantic",
      priority: "medium",
      completed: false,
      dateAdded: "2024-01-05",
      image: "https://images.unsplash.com/photo-1502602898536-47ad22581b52?w=400"
    }
  ]
  
  let selectedFilter = 'all'
  let selectedSort = 'date-added'
  let searchQuery = ''
  
  const categories = [
    { name: "All", emoji: "🌍", color: "#6366f1", value: "all" },
    { name: "Beaches", emoji: "🏖️", color: "#4FC3F7", value: "beaches" },
    { name: "Cities", emoji: "🏙️", color: "#FF7043", value: "cities" },
    { name: "Mountains", emoji: "🏔️", color: "#66BB6A", value: "mountains" },
    { name: "Adventure", emoji: "🧗‍♀️", color: "#AB47BC", value: "adventure" },
    { name: "Romantic", emoji: "💕", color: "#F06292", value: "romantic" }
  ]
  
  const sortOptions = [
    { name: "Date Added", value: "date-added" },
    { name: "Priority", value: "priority" },
    { name: "Title", value: "title" },
    { name: "Category", value: "category" }
  ]
  
  $: filteredItems = bucketListItems.filter(item => {
    const matchesFilter = selectedFilter === 'all' || item.category === selectedFilter
    const matchesSearch = item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         item.description.toLowerCase().includes(searchQuery.toLowerCase())
    const isNotCompleted = !item.completed
    return matchesFilter && matchesSearch && isNotCompleted
  })
  
  $: sortedItems = [...filteredItems].sort((a, b) => {
    switch (selectedSort) {
      case 'priority':
        const priorityOrder = { 'high': 3, 'medium': 2, 'low': 1 }
        return priorityOrder[b.priority] - priorityOrder[a.priority]
      case 'title':
        return a.title.localeCompare(b.title)
      case 'category':
        return a.category.localeCompare(b.category)
      default: // date-added
        return new Date(b.dateAdded) - new Date(a.dateAdded)
    }
  })
  
  $: incompleteItems = bucketListItems.filter(item => !item.completed)
  $: incompleteCount = incompleteItems.length
  $: completedCount = bucketListItems.filter(item => item.completed).length
  $: totalCount = bucketListItems.length
  
  function toggleComplete(item) {
    item.completed = !item.completed
    if (item.completed && !item.completedDate) {
      item.completedDate = new Date().toISOString().split('T')[0]
    }
  }
  
  function getPriorityColor(priority) {
    switch (priority) {
      case 'high': return '#ef4444'
      case 'medium': return '#f59e0b'
      case 'low': return '#10b981'
      default: return '#6b7280'
    }
  }
</script>

<main class="bucket-list-page">
  <!-- Hero Section -->
  <section class="hero">
    <div class="container">
      <div class="hero-content">
        <h1>My Bucket List</h1>
        <p>Dream it. Plan it. Do it.</p>
        <div class="stats">
          <div class="stat-item">
            <span class="stat-number">{incompleteCount}</span>
            <span class="stat-label">Active Goals</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">{categories.length - 1}</span>
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
        <h2>Filter & Sort</h2>
        <div class="filters-controls">
          <div class="search-box">
            <input 
              type="text" 
              placeholder="Search your bucket list..." 
              bind:value={searchQuery}
              class="search-input"
            />
            <span class="search-icon">🔍</span>
          </div>
          <select bind:value={selectedSort} class="sort-select">
            {#each sortOptions as option}
              <option value={option.value}>{option.name}</option>
            {/each}
          </select>
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
          </button>
        {/each}
      </div>
    </div>
  </section>

  <!-- Bucket List Items -->
  <section class="bucket-items">
    <div class="container">
      {#if sortedItems.length === 0}
        <div class="empty-state">
          <div class="empty-icon">📝</div>
          <h3>No items found</h3>
          <p>Try adjusting your search or filters to find what you're looking for.</p>
        </div>
      {:else}
        <div class="items-grid">
          {#each sortedItems as item}
            <div class="bucket-item {item.completed ? 'completed' : ''}">
              <div class="item-image" style={`background-image: url('${item.image}')`}>
                <div class="item-overlay">
                  <button 
                    class="complete-btn {item.completed ? 'completed' : ''}"
                    on:click={() => toggleComplete(item)}
                    aria-label={item.completed ? 'Mark as incomplete' : 'Mark as complete'}
                  >
                    {item.completed ? '✓' : '○'}
                  </button>
                </div>
                <div class="priority-badge" style={`background-color: ${getPriorityColor(item.priority)}`}>
                  {item.priority}
                </div>
              </div>
              <div class="item-content">
                <div class="item-header">
                  <h3 class="item-title">{item.title}</h3>
                  <span class="item-category">{item.category}</span>
                </div>
                <p class="item-description">{item.description}</p>
                <div class="item-footer">
                  <span class="item-date">Added: {new Date(item.dateAdded).toLocaleDateString()}</span>
                  {#if item.completed && item.completedDate}
                    <span class="completed-date">Completed: {new Date(item.completedDate).toLocaleDateString()}</span>
                  {/if}
                </div>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  </section>

  <!-- Add Item CTA -->
  <section class="add-item-cta">
    <div class="container">
      <div class="cta-content">
        <h2>Ready to add more dreams?</h2>
        <p>Start building your ultimate bucket list today</p>
        <button class="add-item-btn" disabled>
          <span class="btn-icon">+</span>
          Add New Item
          <small>(Coming Soon)</small>
        </button>
      </div>
    </div>
  </section>
</main>


