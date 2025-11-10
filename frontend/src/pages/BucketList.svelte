<script>
  import '../styles/bucket-list.css'
  import { getBucketList, createTripForBucketList } from '../lib/api.js'
  import { onMount } from 'svelte'
  
  // Bucket list data from backend
  let bucketListItems = []
  let loading = true
  let error = null
  
  // Form state
  let showAddForm = false
  let formData = {
    name: '',
    location: '',
    date: ''
  }
  let formError = null
  let formLoading = false
  
  // Load bucket list data from backend
  async function loadBucketList() {
    loading = true
    error = null
    try {
      const response = await getBucketList()
      if (response.success && response.trips) {
        // Transform backend data to match UI structure
        bucketListItems = response.trips.map(trip => ({
          id: trip.id,
          title: trip.name || trip.location,
          description: trip.location || `Trip to ${trip.name || 'Unknown'}`,
          category: "adventure", // Default category since backend doesn't have this
          priority: "medium", // Default priority
      completed: false,
          dateAdded: trip.date || new Date().toISOString().split('T')[0],
          image: "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=400" // Default travel image
        }))
      }
    } catch (err) {
      console.error('Error loading bucket list:', err)
      error = err.message || 'Failed to load bucket list'
    } finally {
      loading = false
    }
  }
  
  // Load data when component mounts
  onMount(() => {
    loadBucketList()
  })
  
  // Handle form submission
  async function handleAddTrip() {
    formError = null
    formLoading = true
    
    if (!formData.name || !formData.location) {
      formError = 'Name and location are required'
      formLoading = false
      return
    }
    
    try {
      const response = await createTripForBucketList({
        name: formData.name,
        location: formData.location,
        date: formData.date || null
      })
      
      if (response.success) {
        // Reset form
        formData = { name: '', location: '', date: '' }
        showAddForm = false
        // Reload bucket list
        await loadBucketList()
      }
    } catch (err) {
      formError = err.message || 'Failed to create trip'
    } finally {
      formLoading = false
    }
  }
  
  function openAddForm() {
    showAddForm = true
    formError = null
    formData = { name: '', location: '', date: '' }
  }
  
  function closeAddForm() {
    showAddForm = false
    formError = null
    formData = { name: '', location: '', date: '' }
  }
  
  let selectedFilter = 'all'
  let selectedSort = 'date-added'
  let searchQuery = ''
  let currentPage = 1
  const itemsPerPage = 10
  
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
  
  // Handle empty state when loading or error
  $: hasItems = bucketListItems.length > 0
  
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
  
  // Pagination logic
  $: totalPages = Math.ceil(sortedItems.length / itemsPerPage)
  
  // Reset to page 1 when filters or search change
  $: filterKey = `${selectedFilter}-${selectedSort}-${searchQuery}`
  
  $: startIndex = (currentPage - 1) * itemsPerPage
  $: endIndex = startIndex + itemsPerPage
  $: paginatedItems = sortedItems.slice(startIndex, endIndex)
  
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
  
  let previousFilterKey = ''
  
  function nextPage() {
    if (currentPage < totalPages) {
      currentPage++
    }
  }
  
  function previousPage() {
    if (currentPage > 1) {
      currentPage--
    }
  }
  
  function goToPage(page) {
    currentPage = page
  }
  
  // Reset to page 1 when filters or search change
  $: {
    if (previousFilterKey && previousFilterKey !== filterKey) {
      currentPage = 1
    }
    previousFilterKey = filterKey
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
      {#if loading}
        <div class="empty-state">
          <div class="empty-icon">⏳</div>
          <h3>Loading...</h3>
          <p>Loading your bucket list items...</p>
        </div>
      {:else if error}
        <div class="empty-state">
          <div class="empty-icon">⚠️</div>
          <h3>Error loading bucket list</h3>
          <p>{error}</p>
        </div>
      {:else if sortedItems.length === 0 && hasItems}
        <div class="empty-state">
          <div class="empty-icon">📝</div>
          <h3>No items found</h3>
          <p>Try adjusting your search or filters to find what you're looking for.</p>
        </div>
      {:else if !hasItems}
        <div class="empty-state">
          <div class="empty-icon">📝</div>
          <h3>Your bucket list is empty</h3>
          <p>Start adding trips to your bucket list to see them here!</p>
        </div>
      {:else}
        <div class="items-grid">
          {#each paginatedItems as item}
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
        
        <!-- Pagination Controls -->
        {#if totalPages > 1}
          <div class="pagination">
            <div class="pagination-info">
              Showing {startIndex + 1} - {Math.min(endIndex, sortedItems.length)} of {sortedItems.length} items
            </div>
            <div class="pagination-controls">
              <button 
                class="pagination-btn" 
                on:click={previousPage}
                disabled={currentPage === 1}
              >
                ← Previous
              </button>
              
              <div class="page-numbers">
                {#each Array(totalPages) as _, i}
                  {@const pageNum = i + 1}
                  {#if pageNum === 1 || pageNum === totalPages || (pageNum >= currentPage - 2 && pageNum <= currentPage + 2)}
                    <button
                      class="page-btn {pageNum === currentPage ? 'active' : ''}"
                      on:click={() => goToPage(pageNum)}
                    >
                      {pageNum}
                    </button>
                  {:else if pageNum === currentPage - 3 || pageNum === currentPage + 3}
                    <span class="page-ellipsis">...</span>
                  {/if}
                {/each}
              </div>
              
              <button 
                class="pagination-btn" 
                on:click={nextPage}
                disabled={currentPage === totalPages}
              >
                Next →
              </button>
            </div>
          </div>
        {/if}
      {/if}
    </div>
  </section>

  <!-- Add Item CTA -->
  <section class="add-item-cta">
    <div class="container">
      <div class="cta-content">
        <h2>Ready to add more dreams?</h2>
        <p>Start building your ultimate bucket list today</p>
        <button class="add-item-btn" on:click={openAddForm}>
          <span class="btn-icon">+</span>
          Add New Item
        </button>
      </div>
    </div>
  </section>
</main>

<!-- Add Trip Modal -->
{#if showAddForm}
  <div class="modal-overlay" on:click={closeAddForm}>
    <div class="modal-content" on:click|stopPropagation>
      <div class="modal-header">
        <h2>Add New Trip to Bucket List</h2>
        <button class="modal-close" on:click={closeAddForm}>×</button>
      </div>
      
      <form on:submit|preventDefault={handleAddTrip} class="trip-form">
        {#if formError}
          <div class="form-error">{formError}</div>
        {/if}
        
        <div class="form-group">
          <label for="trip-name">Trip Name *</label>
          <input
            id="trip-name"
            type="text"
            bind:value={formData.name}
            placeholder="e.g., Visit Paris"
            required
            disabled={formLoading}
          />
        </div>
        
        <div class="form-group">
          <label for="trip-location">Location *</label>
          <input
            id="trip-location"
            type="text"
            bind:value={formData.location}
            placeholder="e.g., Paris, France"
            required
            disabled={formLoading}
          />
        </div>
        
        <div class="form-group">
          <label for="trip-date">Date (Optional)</label>
          <input
            id="trip-date"
            type="date"
            bind:value={formData.date}
            disabled={formLoading}
          />
        </div>
        
        <div class="form-actions">
          <button type="button" class="btn-cancel" on:click={closeAddForm} disabled={formLoading}>
            Cancel
          </button>
          <button type="submit" class="btn-submit" disabled={formLoading}>
            {formLoading ? 'Adding...' : 'Add to Bucket List'}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}

<style>
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.6);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: 20px;
  }
  
  .modal-content {
    background: white;
    border-radius: 16px;
    max-width: 500px;
    width: 100%;
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  }
  
  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 24px;
    border-bottom: 1px solid #e5e7eb;
  }
  
  .modal-header h2 {
    margin: 0;
    font-size: 24px;
    color: #1f2937;
  }
  
  .modal-close {
    background: none;
    border: none;
    font-size: 32px;
    color: #6b7280;
    cursor: pointer;
    padding: 0;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
    transition: all 0.2s;
  }
  
  .modal-close:hover {
    background: #f3f4f6;
    color: #1f2937;
  }
  
  .trip-form {
    padding: 24px;
  }
  
  .form-group {
    margin-bottom: 20px;
  }
  
  .form-group label {
    display: block;
    margin-bottom: 8px;
    font-weight: 600;
    color: #374151;
    font-size: 14px;
  }
  
  .form-group input {
    width: 100%;
    padding: 12px;
    border: 2px solid #e5e7eb;
    border-radius: 8px;
    font-size: 16px;
    transition: border-color 0.2s;
    box-sizing: border-box;
  }
  
  .form-group input:focus {
    outline: none;
    border-color: #6366f1;
  }
  
  .form-group input:disabled {
    background: #f3f4f6;
    cursor: not-allowed;
  }
  
  .form-error {
    background: #fee2e2;
    color: #dc2626;
    padding: 12px;
    border-radius: 8px;
    margin-bottom: 20px;
    font-size: 14px;
  }
  
  .form-actions {
    display: flex;
    gap: 12px;
    justify-content: flex-end;
    margin-top: 24px;
  }
  
  .btn-cancel,
  .btn-submit {
    padding: 12px 24px;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    border: none;
  }
  
  .btn-cancel {
    background: #f3f4f6;
    color: #374151;
  }
  
  .btn-cancel:hover:not(:disabled) {
    background: #e5e7eb;
  }
  
  .btn-submit {
    background: #6366f1;
    color: white;
  }
  
  .btn-submit:hover:not(:disabled) {
    background: #4f46e5;
  }
  
  .btn-cancel:disabled,
  .btn-submit:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
</style>


