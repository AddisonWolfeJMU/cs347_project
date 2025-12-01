<script>
  import '../styles/bucket-list.css'
  import { getMyTrips, createTripForMyTrips } from '../lib/api.js'
  import { onMount } from 'svelte'
  
  // Trips data from backend
  let allTrips = []
  let loading = true
  let error = null
  
  // Form state
  let showAddForm = false
  let formData = {
    name: '',
    location: '',
    date: '',
    image: null
  }
  let formError = null
  let formLoading = false
  let imagePreview = null
  
  // Load trips data from backend
  async function loadTrips() {
    loading = true
    error = null
    try {
      const response = await getMyTrips()
      if (response.success && response.trips) {
        // Transform backend data to match UI structure
        allTrips = response.trips.map(trip => ({
          id: trip.id,
          title: trip.name || trip.location,
          description: trip.location || `Trip to ${trip.name || 'Unknown'}`,
          category: "adventure", // Default category since backend doesn't have this
          priority: "medium", // Default priority
          completed: true, // MyTrips are completed trips
          dateAdded: trip.date || new Date().toISOString().split('T')[0],
          completedDate: trip.date || new Date().toISOString().split('T')[0],
          image: trip.image || "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=400" // Use uploaded image or default
        }))
      }
    } catch (err) {
      console.error('Error loading trips:', err)
      error = err.message || 'Failed to load trips'
    } finally {
      loading = false
    }
  }
  
  // Load data when component mounts
  onMount(() => {
    loadTrips()
  })
  
  // Handle image selection
  function handleImageSelect(event) {
    const file = event.target.files[0]
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        formError = 'Please select an image file'
        return
      }
      
      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        formError = 'Image size must be less than 5MB'
        return
      }
      
      formData.image = file
      formError = null
      
      // Create preview
      const reader = new FileReader()
      reader.onload = (e) => {
        imagePreview = e.target.result
      }
      reader.readAsDataURL(file)
    }
  }
  
  function removeImage() {
    formData.image = null
    imagePreview = null
  }
  
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
      const response = await createTripForMyTrips({
        name: formData.name,
        location: formData.location,
        date: formData.date || null,
        image: formData.image
      })
      
      if (response.success) {
        // Reset form
        formData = { name: '', location: '', date: '', image: null }
        imagePreview = null
        showAddForm = false
        // Reload trips
        await loadTrips()
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
    formData = { name: '', location: '', date: '', image: null }
    imagePreview = null
  }
  
  function closeAddForm() {
    showAddForm = false
    formError = null
    formData = { name: '', location: '', date: '', image: null }
    imagePreview = null
  }
  
  // Filter to show only completed trips (all trips in MyTrips are completed)
  $: completedTrips = allTrips.filter(trip => trip.completed)
  
  let searchQuery = ''

  $: filteredTrips = completedTrips.filter(trip => {
    const matchesSearch = trip.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         trip.description.toLowerCase().includes(searchQuery.toLowerCase())
    return matchesSearch
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

  // Export functions
  function exportToJSON() {
    const exportData = {
      exportDate: new Date().toISOString(),
      exportFormat: 'JSON',
      totalItems: allTrips.length,
      items: allTrips.map(trip => ({
        id: trip.id,
        name: trip.title,
        location: trip.description,
        category: trip.category,
        priority: trip.priority,
        completed: trip.completed,
        dateAdded: trip.dateAdded,
        completedDate: trip.completedDate,
        imageUrl: trip.image
      }))
    }

    const dataStr = JSON.stringify(exportData, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `my-trips-export-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  function exportToCSV() {
    // CSV header
    const headers = ['ID', 'Name/Title', 'Location/Description', 'Category', 'Priority', 'Completed', 'Date Added', 'Completed Date', 'Image URL']
    const rows = allTrips.map(trip => [
      trip.id,
      `"${(trip.title || '').replace(/"/g, '""')}"`,
      `"${(trip.description || '').replace(/"/g, '""')}"`,
      trip.category || '',
      trip.priority || '',
      trip.completed ? 'Yes' : 'No',
      trip.dateAdded || '',
      trip.completedDate || '',
      trip.image || ''
    ])

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.join(','))
    ].join('\n')

    // Add BOM for Excel compatibility
    const BOM = '\uFEFF'
    const dataBlob = new Blob([BOM + csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `my-trips-export-${new Date().toISOString().split('T')[0]}.csv`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  let showExportMenu = false

  function toggleExportMenu() {
    showExportMenu = !showExportMenu
  }

  function closeExportMenu() {
    showExportMenu = false
  }
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
        </div>
      </div>
    </div>
  </section>

  <!-- Search -->
  <section class="filters-section">
    <div class="container">
      <div class="filters-header">
        <h2>Search Your Adventures</h2>
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
          <div class="export-container">
            <button class="export-btn" on:click={toggleExportMenu} disabled={allTrips.length === 0}>
              <span class="export-icon">📥</span>
              <span>Export</span>
            </button>
            {#if showExportMenu}
              <div class="export-menu" on:click|stopPropagation>
                <button class="export-option" on:click={() => { exportToJSON(); closeExportMenu(); }}>
                  <span class="export-option-icon">📄</span>
                  <span>Export as JSON</span>
                </button>
                <button class="export-option" on:click={() => { exportToCSV(); closeExportMenu(); }}>
                  <span class="export-option-icon">📊</span>
                  <span>Export as CSV</span>
                </button>
              </div>
            {/if}
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Completed Trips -->
  <section class="bucket-items">
    <div class="container">
      {#if loading}
        <div class="empty-state">
          <div class="empty-icon">⏳</div>
          <h3>Loading...</h3>
          <p>Loading your trips...</p>
        </div>
      {:else if error}
        <div class="empty-state">
          <div class="empty-icon">⚠️</div>
          <h3>Error loading trips</h3>
          <p>{error}</p>
        </div>
      {:else if sortedTrips.length === 0}
        <div class="empty-state">
          <div class="empty-icon">✈️</div>
          <h3>No trips yet</h3>
          <p>Start your journey by adding items to your bucket list and completing your first adventure!</p>
        </div>
      {:else}
        <div class="items-grid">
          {#each sortedTrips as trip}
            <div class="bucket-item completed" on:click={() => window.location.hash = `#trip/${trip.id}`} style="cursor: pointer;" role="button" tabindex="0">
              <div class="item-image" style={`background-image: url('${trip.image}')`}>
                <div class="priority-badge" style={`background-color: ${getPriorityColor(trip.priority)}`}>
                  {trip.priority}
                </div>
                <div class="completed-badge">✓ Completed</div>
              </div>
              <div class="item-content">
                <div class="item-header">
                  <h3 class="item-title">{trip.title}</h3>
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
        <p>Your journey doesn't end here. Add more completed trips to your collection</p>
        <button class="add-item-btn" on:click={openAddForm}>
          <span class="btn-icon">+</span>
          Add Completed Trip
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
        <h2>Add Completed Trip</h2>
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
        
        <div class="form-group">
          <label for="trip-image">Cover Photo (Optional)</label>
          {#if imagePreview}
            <div class="image-preview-container">
              <img src={imagePreview} alt="Preview" class="image-preview" />
              <button type="button" class="remove-image-btn" on:click={removeImage}>Remove</button>
            </div>
          {:else}
            <input
              id="trip-image"
              type="file"
              accept="image/*"
              on:change={handleImageSelect}
              disabled={formLoading}
              class="file-input"
            />
            <small class="file-hint">Max size: 5MB. Supported formats: JPG, PNG, GIF</small>
          {/if}
        </div>
        
        <div class="form-actions">
          <button type="button" class="btn-cancel" on:click={closeAddForm} disabled={formLoading}>
            Cancel
          </button>
          <button type="submit" class="btn-submit" disabled={formLoading}>
            {formLoading ? 'Adding...' : 'Add to My Trips'}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}

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
  
  .add-item-btn {
    margin-top: 20px;
  }
  
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
  
  .file-input {
    width: 100%;
    padding: 12px;
    border: 2px dashed #e5e7eb;
    border-radius: 8px;
    font-size: 16px;
    cursor: pointer;
    transition: border-color 0.2s;
  }
  
  .file-input:hover:not(:disabled) {
    border-color: #6366f1;
  }
  
  .file-input:disabled {
    background: #f3f4f6;
    cursor: not-allowed;
  }
  
  .file-hint {
    display: block;
    margin-top: 8px;
    color: #6b7280;
    font-size: 12px;
  }
  
  .image-preview-container {
    position: relative;
    margin-top: 8px;
  }
  
  .image-preview {
    width: 100%;
    max-height: 200px;
    object-fit: cover;
    border-radius: 8px;
    border: 2px solid #e5e7eb;
  }
  
  .remove-image-btn {
    position: absolute;
    top: 8px;
    right: 8px;
    background: rgba(220, 38, 38, 0.9);
    color: white;
    border: none;
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
  }
  
  .remove-image-btn:hover {
    background: rgba(220, 38, 38, 1);
  }
</style>
