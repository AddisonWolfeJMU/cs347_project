<script>
  import '../styles/bucket-list.css'
  import { getBucketList, createTripForBucketList } from '../lib/api.js'
  import { onMount } from 'svelte'
  
  // Bucket list data from backend
  let bucketListItems = []
  let loading = true
  let error = null
  
  // Multi-step form state
  let showAddForm = false
  let currentStep = 1
  const totalSteps = 3
  let formData = {
    name: '',
    location: '',
    date: '',
    image: null,
    notes: ''
  }
  let formError = null
  let formLoading = false
  let imagePreview = null
  let stepErrors = {
    step1: {},
    step2: {},
    step3: {}
  }
  
  // Load bucket list data from backend
  async function loadBucketList() {
    loading = true
    error = null
    try {
      const response = await getBucketList()
      if (response.success && response.trips) {
        // Transform backend data to match UI structure
        bucketListItems = response.trips.map(trip => {
          // Handle image URL - use fallback if image is null, empty, or invalid
          let imageUrl = trip.image
          
          // Debug: log the image URL to see what we're getting
          console.log(`Trip ${trip.id} image URL:`, imageUrl)
          
          if (!imageUrl || imageUrl === 'null' || imageUrl === 'undefined' || imageUrl.trim() === '') {
            imageUrl = "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=400"
          }
          
          return {
            id: trip.id,
            title: trip.name || trip.location,
            description: trip.location || `Trip to ${trip.name || 'Unknown'}`,
            category: "adventure", // Default category since backend doesn't have this
            completed: false,
            dateAdded: trip.date || new Date().toISOString().split('T')[0],
            image: imageUrl
          }
        })
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
    
    // Close export menu when clicking outside
    if (typeof window !== 'undefined') {
      const handleClickOutside = (event) => {
        if (showExportMenu && !event.target.closest('.export-container')) {
          closeExportMenu()
        }
      }
      window.addEventListener('click', handleClickOutside)
      return () => {
        window.removeEventListener('click', handleClickOutside)
      }
    }
  })
  
  // Handle image selection
  function handleImageSelect(event) {
    const file = event.target.files[0]
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        formError = 'Please select an image file (png, jpg or gif)'
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
  
  // Multi-step form navigation
  function validateStep(step) {
    stepErrors[`step${step}`] = {}
    let isValid = true
    
    if (step === 1) {
      if (!formData.name || formData.name.trim() === '') {
        stepErrors.step1.name = 'Trip name is required'
        isValid = false
      }
      if (!formData.location || formData.location.trim() === '') {
        stepErrors.step1.location = 'Location is required'
        isValid = false
      }
    }
    
    return isValid
  }
  
  function nextStep() {
    if (validateStep(currentStep)) {
      if (currentStep < totalSteps) {
        currentStep++
        formError = null
      }
    }
  }
  
  function previousStep() {
    if (currentStep > 1) {
      currentStep--
      formError = null
    }
  }
  
  // Handle form submission
  async function handleAddTrip() {
    formError = null
    formLoading = true
    
    // Final validation
    if (!validateStep(1)) {
      currentStep = 1
      formLoading = false
      return
    }
    
    try {
      const response = await createTripForBucketList({
        name: formData.name,
        location: formData.location,
        date: formData.date || null,
        image: formData.image
      })
      
      if (response.success) {
        // Reset form
        formData = { name: '', location: '', date: '', image: null, notes: '' }
        imagePreview = null
        currentStep = 1
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
    currentStep = 1
    formError = null
    formData = { name: '', location: '', date: '', image: null, notes: '' }
    imagePreview = null
    stepErrors = { step1: {}, step2: {}, step3: {} }
  }
  
  function closeAddForm() {
    showAddForm = false
    currentStep = 1
    formError = null
    formData = { name: '', location: '', date: '', image: null, notes: '' }
    imagePreview = null
    stepErrors = { step1: {}, step2: {}, step3: {} }
  }
  
  let selectedSort = 'date-added'
  let searchQuery = ''
  let currentPage = 1
  const itemsPerPage = 10
  
  const sortOptions = [
    { name: "Date Added", value: "date-added" },
    { name: "Title", value: "title" },
    { name: "Category", value: "category" }
  ]
  
  $: filteredItems = bucketListItems.filter(item => {
    const matchesSearch = item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         item.description.toLowerCase().includes(searchQuery.toLowerCase())
    const isNotCompleted = !item.completed
    return matchesSearch && isNotCompleted
  })
  
  // Handle empty state when loading or error
  $: hasItems = bucketListItems.length > 0
  
  $: sortedItems = [...filteredItems].sort((a, b) => {
    switch (selectedSort) {

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
  
  // Reset to page 1 when sort or search change
  $: filterKey = `${selectedSort}-${searchQuery}`
  
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

  // Export functions
  function exportToJSON() {
    const exportData = {
      exportDate: new Date().toISOString(),
      exportFormat: 'JSON',
      totalItems: bucketListItems.length,
      items: bucketListItems.map(item => ({
        id: item.id,
        name: item.title, // Backend field name
        location: item.description, // Backend field name
        title: item.title, // UI field name
        description: item.description, // UI field name
        category: item.category,
        completed: item.completed,
        dateAdded: item.dateAdded,
        date: item.dateAdded, // Backend field name
        completedDate: item.completedDate || null,
        imageUrl: item.image
      }))
    }
    
    const dataStr = JSON.stringify(exportData, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `bucket-list-export-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  function exportToCSV() {
    // CSV header
    const headers = ['ID', 'Name/Title', 'Location/Description', 'Category', 'Completed', 'Date Added', 'Completed Date', 'Image URL']
    const rows = bucketListItems.map(item => [
      item.id,
      `"${(item.title || '').replace(/"/g, '""')}"`,
      `"${(item.description || '').replace(/"/g, '""')}"`,
      item.category || '',
      item.completed ? 'Yes' : 'No',
      item.dateAdded || '',
      item.completedDate || '',
      item.image || ''
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
    link.download = `bucket-list-export-${new Date().toISOString().split('T')[0]}.csv`
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
        <h1>My Bucket List</h1>
        <p>Dream it. Plan it. Do it.</p>
        <div class="stats">
          <div class="stat-item">
            <span class="stat-number">{incompleteCount}</span>
            <span class="stat-label">Active Goals</span>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Search and Sort -->
  <section class="filters-section">
    <div class="container">
      <div class="filters-header">
        <h2>Search & Sort</h2>
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
          <div class="export-container">
            <button class="export-btn" on:click={toggleExportMenu} disabled={bucketListItems.length === 0}>
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
            <div class="bucket-item {item.completed ? 'completed' : ''}" on:click={() => window.location.hash = `#trip/${item.id}`} style="cursor: pointer;">
              <div class="item-image" style={`background-image: url('${item.image || "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=400"}')`}>
                
              </div>
              <div class="item-content">
                <div class="item-header">
                  <h3 class="item-title">{item.title}</h3>
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

<!-- Multi-Step Add Trip Modal -->
{#if showAddForm}
  <div class="modal-overlay" on:click={closeAddForm}>
    <div class="modal-content multi-step-form" on:click|stopPropagation>
      <div class="modal-header">
        <h2>Add New Trip to Bucket List</h2>
        <button class="modal-close" on:click={closeAddForm}>×</button>
      </div>
      
      <!-- Progress Indicator -->
      <div class="step-indicator">
        {#each Array(totalSteps) as _, i}
          {@const stepNum = i + 1}
          <div class="step-item {currentStep >= stepNum ? 'active' : ''} {currentStep > stepNum ? 'completed' : ''}">
            <div class="step-number">
              {#if currentStep > stepNum}
                ✓
              {:else}
                {stepNum}
              {/if}
            </div>
            <div class="step-label">
              {stepNum === 1 ? 'Basic Info' : stepNum === 2 ? 'Details' : 'Review'}
            </div>
          </div>
          {#if stepNum < totalSteps}
            <div class="step-connector {currentStep > stepNum ? 'completed' : ''}"></div>
          {/if}
        {/each}
      </div>

      
      <form on:submit|preventDefault={handleAddTrip} class="trip-form">
        {#if formError}
          <div class="form-error">{formError}</div>
        {/if}
        
        <!-- Step 1: Basic Information -->
        {#if currentStep === 1}
          <div class="step-content">
            <h3 class="step-title">Basic Information</h3>
            <p class="step-description">Tell us about your dream destination</p>
            
            <div class="form-group">
              <label for="trip-name">Trip Name *</label>
              <input
                id="trip-name"
                type="text"
                bind:value={formData.name}
                placeholder="e.g., Visit Paris"
                class={stepErrors.step1.name ? 'error' : ''}
                disabled={formLoading}
              />
              {#if stepErrors.step1.name}
                <span class="field-error">{stepErrors.step1.name}</span>
              {/if}
            </div>
            
            <div class="form-group">
              <label for="trip-location">Location *</label>
              <input
                id="trip-location"
                type="text"
                bind:value={formData.location}
                placeholder="e.g., Paris, France"
                class={stepErrors.step1.location ? 'error' : ''}
                disabled={formLoading}
              />
              {#if stepErrors.step1.location}
                <span class="field-error">{stepErrors.step1.location}</span>
              {/if}
            </div>
            
            <div class="form-group">
              <label for="trip-date">Planned Date</label>
              <input
                id="trip-date"
                type="date"
                bind:value={formData.date}
                disabled={formLoading}
              />
              <small class="field-hint">When do you plan to visit?</small>
            </div>
          </div>
        {/if}
        
        <!-- Step 2: Visual & Details -->
        {#if currentStep === 2}
          <div class="step-content">
            <h3 class="step-title">Visual & Details</h3>
            <p class="step-description">Add a photo and any additional notes</p>
            
            <div class="form-group">
              <label for="trip-image">Cover Photo (Optional)</label>
              {#if imagePreview}
                <div class="image-preview-container">
                  <img src={imagePreview} alt="Preview" class="image-preview" />
                  <button type="button" class="remove-image-btn" on:click={removeImage}>Remove</button>
                </div>
              {:else}
                <div class="file-upload-area">
                  <input
                    id="trip-image"
                    type="file"
                    accept="image/*"
                    on:change={handleImageSelect}
                    disabled={formLoading}
                    class="file-input-hidden"
                  />
                  <label for="trip-image" class="file-upload-label">
                    <span class="upload-icon">📷</span>
                    <span class="upload-text">Click to upload or drag and drop</span>
                    <span class="upload-hint">Max size: 5MB. Supported formats: JPG, PNG, GIF</span>
                  </label>
                </div>
              {/if}
            </div>
            
            <div class="form-group">
              <label for="trip-notes">Notes (Optional)</label>
              <textarea
                id="trip-notes"
                bind:value={formData.notes}
                placeholder="Add any notes, ideas, or inspiration for this trip..."
                rows="4"
                disabled={formLoading}
                class="form-textarea"
              ></textarea>
              <small class="field-hint">What makes this trip special to you?</small>
            </div>
          </div>
        {/if}
        
        <!-- Step 3: Review & Submit -->
        {#if currentStep === 3}
          <div class="step-content">
            <h3 class="step-title">Review Your Trip</h3>
            <p class="step-description">Please review your information before submitting</p>
            
            <div class="review-summary">
              <div class="review-item">
                <span class="review-label">Trip Name:</span>
                <span class="review-value">{formData.name || 'Not set'}</span>
              </div>
              <div class="review-item">
                <span class="review-label">Location:</span>
                <span class="review-value">{formData.location || 'Not set'}</span>
              </div>
              <div class="review-item">
                <span class="review-label">Planned Date:</span>
                <span class="review-value">
                  {formData.date ? new Date(formData.date).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }) : 'Not set'}
                </span>
              </div>
              <div class="review-item">
                <span class="review-label">Cover Photo:</span>
                <span class="review-value">{formData.image ? '✓ Uploaded' : 'Not uploaded'}</span>
              </div>
              {#if formData.notes}
                <div class="review-item">
                  <span class="review-label">Notes:</span>
                  <span class="review-value notes-value">{formData.notes}</span>
                </div>
              {/if}
            </div>
            
            {#if imagePreview}
              <div class="review-image">
                <img src={imagePreview} alt="Trip preview" />
              </div>
            {/if}
          </div>
        {/if}
        
        <!-- Navigation Buttons -->
        <div class="form-actions">
          <div class="form-actions-left">
            {#if currentStep > 1}
              <button type="button" class="btn-back" on:click={previousStep} disabled={formLoading}>
                ← Previous
              </button>
            {:else}
              <button type="button" class="btn-cancel" on:click={closeAddForm} disabled={formLoading}>
                Cancel
              </button>
            {/if}
          </div>
          
          <div class="form-actions-right">
            {#if currentStep < totalSteps}
              <button type="button" class="btn-next" on:click={nextStep} disabled={formLoading}>
                Next →
              </button>
            {:else}
              <button type="submit" class="btn-submit" disabled={formLoading}>
                {formLoading ? 'Adding...' : 'Add to Bucket List'}
              </button>
            {/if}
          </div>
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
  
  /* Multi-Step Form Styles */
  .multi-step-form {
    max-width: 600px;
  }
  
  .step-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 24px;
    border-bottom: 1px solid #e5e7eb;
    background: #f9fafb;
  }
  
  .step-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    position: relative;
  }
  
  .step-number {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: #e5e7eb;
    color: #6b7280;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 16px;
    transition: all 0.3s ease;
  }
  
  .step-item.active .step-number {
    background: #6366f1;
    color: white;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
  }
  
  .step-item.completed .step-number {
    background: #10b981;
    color: white;
  }
  
  .step-label {
    font-size: 12px;
    color: #6b7280;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  
  .step-item.active .step-label {
    color: #6366f1;
  }
  
  .step-item.completed .step-label {
    color: #10b981;
  }
  
  .step-connector {
    width: 60px;
    height: 2px;
    background: #e5e7eb;
    margin: 0 10px;
    transition: background 0.3s ease;
  }
  
  .step-connector.completed {
    background: #10b981;
  }
  
  .step-content {
    padding: 24px;
    min-height: 300px;
  }
  
  .step-title {
    font-size: 24px;
    font-weight: 700;
    color: #1f2937;
    margin: 0 0 8px 0;
  }
  
  .step-description {
    color: #6b7280;
    margin: 0 0 32px 0;
    font-size: 14px;
  }
  
  .form-group textarea.form-textarea {
    width: 100%;
    padding: 12px;
    border: 2px solid #e5e7eb;
    border-radius: 8px;
    font-size: 16px;
    font-family: inherit;
    resize: vertical;
    transition: border-color 0.2s;
    box-sizing: border-box;
  }
  
  .form-group textarea.form-textarea:focus {
    outline: none;
    border-color: #6366f1;
  }
  
  .form-group textarea.form-textarea:disabled {
    background: #f3f4f6;
    cursor: not-allowed;
  }
  
  .field-error {
    display: block;
    color: #dc2626;
    font-size: 12px;
    margin-top: 4px;
  }
  
  .field-hint {
    display: block;
    color: #6b7280;
    font-size: 12px;
    margin-top: 4px;
  }
  
  .form-group input.error {
    border-color: #dc2626;
  }
  
  .file-upload-area {
    border: 2px dashed #e5e7eb;
    border-radius: 8px;
    padding: 32px;
    text-align: center;
    transition: all 0.3s ease;
    cursor: pointer;
  }
  
  .file-upload-area:hover {
    border-color: #6366f1;
    background: #f9fafb;
  }
  
  .file-input-hidden {
    display: none;
  }
  
  .file-upload-label {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    cursor: pointer;
  }
  
  .upload-icon {
    font-size: 48px;
    margin-bottom: 8px;
  }
  
  .upload-text {
    font-weight: 600;
    color: #374151;
    font-size: 16px;
  }
  
  .upload-hint {
    color: #6b7280;
    font-size: 12px;
  }
  
  .review-summary {
    background: #f9fafb;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 24px;
  }
  
  .review-item {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding: 12px 0;
    border-bottom: 1px solid #e5e7eb;
  }
  
  .review-item:last-child {
    border-bottom: none;
  }
  
  .review-label {
    font-weight: 600;
    color: #374151;
    min-width: 120px;
  }
  
  .review-value {
    color: #6b7280;
    text-align: right;
    flex: 1;
  }
  
  .review-value.notes-value {
    text-align: left;
    font-style: italic;
    white-space: pre-wrap;
  }
  
  .review-image {
    margin-top: 24px;
    text-align: center;
  }
  
  .review-image img {
    max-width: 100%;
    max-height: 200px;
    border-radius: 8px;
    border: 2px solid #e5e7eb;
  }
  
  .form-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 24px;
    border-top: 1px solid #e5e7eb;
    gap: 12px;
  }
  
  .form-actions-left,
  .form-actions-right {
    display: flex;
    gap: 12px;
  }
  
  .btn-back {
    padding: 12px 24px;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    border: 2px solid #e5e7eb;
    background: white;
    color: #374151;
  }
  
  .btn-back:hover:not(:disabled) {
    background: #f9fafb;
    border-color: #6366f1;
    color: #6366f1;
  }
  
  .btn-next {
    padding: 12px 24px;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    border: none;
    background: #6366f1;
    color: white;
  }
  
  .btn-next:hover:not(:disabled) {
    background: #4f46e5;
    transform: translateX(2px);
  }
  
  .btn-back:disabled,
  .btn-next:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  /* Responsive adjustments for multi-step form */
  @media (max-width: 768px) {
    .multi-step-form {
      max-width: 95%;
    }
    
    .step-indicator {
      padding: 16px;
    }
    
    .step-number {
      width: 32px;
      height: 32px;
      font-size: 14px;
    }
    
    .step-label {
      font-size: 10px;
    }
    
    .step-connector {
      width: 30px;
      margin: 0 5px;
    }
    
    .step-content {
      padding: 16px;
      min-height: 250px;
    }
    
    .form-actions {
      flex-direction: column;
      gap: 12px;
    }
    
    .form-actions-left,
    .form-actions-right {
      width: 100%;
    }
    
    .btn-back,
    .btn-next,
    .btn-cancel,
    .btn-submit {
      width: 100%;
    }
  }
</style>


