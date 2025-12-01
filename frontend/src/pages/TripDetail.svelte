<script>
  import { onMount } from 'svelte'
  import { getTrip, createPlan, deletePlan, createBNB, updateBNB, createRating, createReview, completeTrip, updateTrip, deleteTrip } from '../lib/api.js'
  
  let tripId = null
  let trip = null
  let loading = true
  let error = null
  let isCompleted = false
  
  // Plan form state
  let showPlanForm = false
  let planFormData = { name: '', activity: '' }
  let planFormError = null
  let planFormLoading = false
  
  // BNB form state
  let showBNBForm = false
  let bnbFormData = { name: '', address: '' }
  let bnbFormError = null
  let bnbFormLoading = false
  
  // Rating/Review form state
  let showReviewForm = false
  let reviewFormData = { statement: '', rating_value: 5 }
  let reviewFormError = null
  let reviewFormLoading = false

  // Edit trip form state
  let showEditTripForm = false
  let editTripFormData = { name: '', location: '', date: '' }
  let editTripFormError = null
  let editTripFormLoading = false
  
  onMount(() => {
    // Get trip ID from URL hash
    const hash = window.location.hash
    const match = hash.match(/trip\/(\d+)/)
    if (match) {
      tripId = parseInt(match[1])
      loadTrip()
    } else {
      error = 'Invalid trip ID'
      loading = false
    }
  })
  
  async function loadTrip() {
    loading = true
    error = null
    try {
      const response = await getTrip(tripId)
      if (response.success) {
        trip = response.trip
        isCompleted = response.trip.is_completed || false
      }
    } catch (err) {
      console.error('Error loading trip:', err)
      error = err.message || 'Failed to load trip'
    } finally {
      loading = false
    }
  }
  
  function goBack() {
    window.history.back()
  }
  
  // Plan functions
  function openPlanForm() {
    showPlanForm = true
    planFormData = { name: '', activity: '' }
    planFormError = null
  }
  
  function closePlanForm() {
    showPlanForm = false
    planFormData = { name: '', activity: '' }
    planFormError = null
  }
  
  async function handleAddPlan() {
    planFormError = null
    planFormLoading = true
    
    if (!planFormData.name) {
      planFormError = 'Plan name is required'
      planFormLoading = false
      return
    }
    
    try {
      const response = await createPlan(tripId, planFormData)
      if (response.success) {
        closePlanForm()
        await loadTrip()
      }
    } catch (err) {
      planFormError = err.message || 'Failed to create plan'
    } finally {
      planFormLoading = false
    }
  }
  
  async function handleDeletePlan(planId) {
    if (!confirm('Are you sure you want to delete this plan?')) {
      return
    }
    
    try {
      await deletePlan(planId)
      await loadTrip()
    } catch (err) {
      alert(err.message || 'Failed to delete plan')
    }
  }
  
  // BNB functions
  function openBNBForm() {
    if (trip.bnb) {
      // Edit existing BNB
      bnbFormData = {
        name: trip.bnb.name,
        address: trip.bnb.address
      }
    } else {
      // Create new BNB
      bnbFormData = { name: '', address: '' }
    }
    showBNBForm = true
    bnbFormError = null
  }
  
  function closeBNBForm() {
    showBNBForm = false
    bnbFormData = { name: '', address: '' }
    bnbFormError = null
  }
  
  async function handleSaveBNB() {
    bnbFormError = null
    bnbFormLoading = true
    
    if (!bnbFormData.name || !bnbFormData.address) {
      bnbFormError = 'Name and address are required'
      bnbFormLoading = false
      return
    }
    
    try {
      if (trip.bnb) {
        // Update existing
        await updateBNB(trip.bnb.id, bnbFormData)
      } else {
        // Create new
        await createBNB(tripId, bnbFormData)
      }
      closeBNBForm()
      await loadTrip()
    } catch (err) {
      bnbFormError = err.message || 'Failed to save BNB'
    } finally {
      bnbFormLoading = false
    }
  }
  
  // Review functions
  function openReviewForm() {
    showReviewForm = true
    reviewFormData = { statement: '', rating_value: 5 }
    reviewFormError = null
  }
  
  function closeReviewForm() {
    showReviewForm = false
    reviewFormData = { statement: '', rating_value: 5 }
    reviewFormError = null
  }
  
  async function handleAddReview() {
    reviewFormError = null
    reviewFormLoading = true
    
    if (!reviewFormData.statement) {
      reviewFormError = 'Review statement is required'
      reviewFormLoading = false
      return
    }
    
    try {
      // First create rating
      const ratingResponse = await createRating(trip.bnb.id, reviewFormData.rating_value)
      if (ratingResponse.success) {
        // Then create review with rating
        await createReview(trip.bnb.id, {
          statement: reviewFormData.statement,
          rating_id: ratingResponse.rating.id
        })
        closeReviewForm()
        await loadTrip()
      }
    } catch (err) {
      reviewFormError = err.message || 'Failed to add review'
    } finally {
      reviewFormLoading = false
    }
  }
  
  function formatDate(dateString) {
    if (!dateString) return 'Not set'
    return new Date(dateString).toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    })
  }

  // Mark trip as completed
  async function handleCompleteTrip() {
    if (!confirm('Mark this trip as completed and move it to My Trips?')) {
      return
    }

    try {
      await completeTrip(tripId)
      await loadTrip()
      alert('Trip marked as completed and moved to My Trips!')
    } catch (err) {
      alert(err.message || 'Failed to complete trip')
    }
  }

  function openEditTripForm() {
    if (trip) {
      editTripFormData = {
        name: trip.name || '',
        location: trip.location || '',
        date: trip.date || ''
      }
      editTripFormError = null
      showEditTripForm = true
    }
  }

  function closeEditTripForm() {
    showEditTripForm = false
    editTripFormLoading = false
    editTripFormError = null
  }

  async function handleSaveTrip() {
    editTripFormError = null
    editTripFormLoading = true

    if (!editTripFormData.name || !editTripFormData.location) {
      editTripFormError = 'Name and location are required'
      editTripFormLoading = false
      return
    }

    try {
      await updateTrip(tripId, {
        name: editTripFormData.name,
        location: editTripFormData.location,
        date: editTripFormData.date || ''
      })
      await loadTrip()
      closeEditTripForm()
    } catch (err) {
      editTripFormError = err.message || 'Failed to update trip'
    } finally {
      editTripFormLoading = false
    }
  }

  async function handleDeleteTrip() {
    if (!confirm('Are you sure you want to delete this trip? This cannot be undone.')) {
      return
    }

    try {
      await deleteTrip(tripId)
      alert('Trip deleted.')
      // Navigate back to My Trips list (route key is 'trips')
      window.location.hash = '#trips'
    } catch (err) {
      alert(err.message || 'Failed to delete trip')
    }
  }
</script>

{#if loading}
  <main class="trip-detail-page">
    <div class="container">
      <div class="loading-state">
        <div class="spinner">⏳</div>
        <p>Loading trip details...</p>
      </div>
    </div>
  </main>
{:else if error}
  <main class="trip-detail-page">
    <div class="container">
      <div class="error-state">
        <h2>Error</h2>
        <p>{error}</p>
        <button class="btn-back" on:click={goBack}>Go Back</button>
      </div>
    </div>
  </main>
{:else if trip}
  <main class="trip-detail-page">
    <div class="container">
      <!-- Header -->
      <div class="trip-header">
        <button class="btn-back" on:click={goBack}>← Back</button>
        <div class="trip-hero">
          {#if trip.image}
            <div class="trip-image" style={`background-image: url('${trip.image}')`}></div>
          {:else}
            <div class="trip-image" style="background-image: url('https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=1200')"></div>
          {/if}
          <div class="trip-info">
            <div class="trip-status-row">
              <div class="trip-status-badge">
                {#if isCompleted}
                  <span class="status-completed">✓ Completed Trip</span>
                {:else}
                  <span class="status-planned">📝 Planned Trip</span>
                {/if}
              </div>
              <div class="trip-actions">
                <button class="btn-outline-light" on:click={openEditTripForm}>
                  ✏️ Edit
                </button>
                <button class="btn-outline-danger" on:click={handleDeleteTrip}>
                  🗑 Delete
                </button>
              </div>
            </div>
            <h1>{trip.name}</h1>
            <p class="trip-location">📍 {trip.location}</p>
            <p class="trip-date">📅 {formatDate(trip.date)}</p>
            {#if !isCompleted}
              <button class="btn-complete" on:click={handleCompleteTrip}>
                ✓ Mark as Completed
              </button>
            {/if}
          </div>
        </div>
      </div>
      
      <!-- Plans Section -->
      <section class="section">
        <div class="section-header">
          <h2>Plans & Activities</h2>
          <button class="btn-add" on:click={openPlanForm}>+ Add Plan</button>
        </div>
        
        {#if trip.plans && trip.plans.length > 0}
          <div class="plans-grid">
            {#each trip.plans as plan}
              <div class="plan-card">
                <div class="plan-content">
                  <h3>{plan.name}</h3>
                  {#if plan.activity}
                    <p>{plan.activity}</p>
                  {/if}
                </div>
                <button class="btn-delete" on:click={() => handleDeletePlan(plan.id)}>Delete</button>
              </div>
            {/each}
          </div>
        {:else}
          <div class="empty-state">
            <p>No plans yet. Add your first plan!</p>
          </div>
        {/if}
      </section>
      
      <!-- BNB Section -->
      <section class="section">
        <div class="section-header">
          <h2>Accommodation (BNB)</h2>
          <button class="btn-add" on:click={openBNBForm}>
            {trip.bnb ? 'Edit' : '+ Add BNB'}
          </button>
        </div>
        
        {#if trip.bnb}
          <div class="bnb-card">
            <div class="bnb-info">
              <h3>{trip.bnb.name}</h3>
              <p class="bnb-address">📍 {trip.bnb.address}</p>
              {#if trip.bnb.average_rating && isCompleted}
                <p class="bnb-rating">⭐ {trip.bnb.average_rating}/5.0</p>
              {/if}
            </div>
            
            <!-- Ratings and Reviews (only for completed trips) -->
            {#if isCompleted}
              {#if trip.bnb.ratings && trip.bnb.ratings.length > 0}
                <div class="ratings-section">
                  <h4>Ratings</h4>
                  <div class="ratings-list">
                    {#each trip.bnb.ratings as rating}
                      <span class="rating-badge">⭐ {rating.value}/5</span>
                    {/each}
                  </div>
                </div>
              {/if}
              
              <!-- Reviews (only for completed trips) -->
              {#if trip.bnb.reviews && trip.bnb.reviews.length > 0}
                <div class="reviews-section">
                  <h4>Reviews</h4>
                  <div class="reviews-list">
                    {#each trip.bnb.reviews as review}
                      <div class="review-item">
                        <p>{review.statement}</p>
                        
                      </div>
                    {/each}
                  </div>
                </div>
              {/if}
              
              <button class="btn-add-review" on:click={openReviewForm}>+ Add Review</button>
            {:else}
              <div class="info-message">
                <p>💡 Complete this trip to add ratings and reviews for your accommodation!</p>
              </div>
            {/if}
          </div>
        {:else}
          <div class="empty-state">
            <p>No accommodation added yet. Add your BNB!</p>
          </div>
        {/if}
      </section>
    </div>
  </main>
{/if}

<!-- Plan Form Modal -->
{#if showPlanForm}
  <div class="modal-overlay" on:click={closePlanForm}>
    <div class="modal-content" on:click|stopPropagation>
      <div class="modal-header">
        <h2>Add Plan</h2>
        <button class="modal-close" on:click={closePlanForm}>×</button>
      </div>
      
      <form on:submit|preventDefault={handleAddPlan} class="form">
        {#if planFormError}
          <div class="form-error">{planFormError}</div>
        {/if}
        
        <div class="form-group">
          <label>Plan Name *</label>
          <input type="text" bind:value={planFormData.name} required disabled={planFormLoading} />
        </div>
        
        <div class="form-group">
          <label>Activity Details</label>
          <textarea bind:value={planFormData.activity} disabled={planFormLoading} rows="4"></textarea>
        </div>
        
        <div class="form-actions">
          <button type="button" class="btn-cancel" on:click={closePlanForm} disabled={planFormLoading}>Cancel</button>
          <button type="submit" class="btn-submit" disabled={planFormLoading}>
            {planFormLoading ? 'Adding...' : 'Add Plan'}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}

<!-- BNB Form Modal -->
{#if showBNBForm}
  <div class="modal-overlay" on:click={closeBNBForm}>
    <div class="modal-content" on:click|stopPropagation>
      <div class="modal-header">
        <h2>{trip.bnb ? 'Edit' : 'Add'} BNB</h2>
        <button class="modal-close" on:click={closeBNBForm}>×</button>
      </div>
      
      <form on:submit|preventDefault={handleSaveBNB} class="form">
        {#if bnbFormError}
          <div class="form-error">{bnbFormError}</div>
        {/if}
        
        <div class="form-group">
          <label>BNB Name *</label>
          <input type="text" bind:value={bnbFormData.name} required disabled={bnbFormLoading} />
        </div>
        
        <div class="form-group">
          <label>Address *</label>
          <input type="text" bind:value={bnbFormData.address} required disabled={bnbFormLoading} />
        </div>
        
        <div class="form-actions">
          <button type="button" class="btn-cancel" on:click={closeBNBForm} disabled={bnbFormLoading}>Cancel</button>
          <button type="submit" class="btn-submit" disabled={bnbFormLoading}>
            {bnbFormLoading ? 'Saving...' : 'Save'}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}

<!-- Edit Trip Modal -->
{#if showEditTripForm}
  <div class="modal-overlay" on:click={closeEditTripForm}>
    <div class="modal-content" on:click|stopPropagation>
      <div class="modal-header">
        <h2>Edit Trip</h2>
        <button class="modal-close" on:click={closeEditTripForm}>×</button>
      </div>

      <form on:submit|preventDefault={handleSaveTrip} class="form">
        {#if editTripFormError}
          <div class="form-error">{editTripFormError}</div>
        {/if}

        <div class="form-group">
          <label>Trip Name *</label>
          <input
            type="text"
            bind:value={editTripFormData.name}
            required
            disabled={editTripFormLoading}
          />
        </div>

        <div class="form-group">
          <label>Location *</label>
          <input
            type="text"
            bind:value={editTripFormData.location}
            required
            disabled={editTripFormLoading}
          />
        </div>

        <div class="form-group">
          <label>Date</label>
          <input
            type="date"
            bind:value={editTripFormData.date}
            disabled={editTripFormLoading}
          />
        </div>

        <div class="form-actions">
          <button type="button" class="btn-cancel" on:click={closeEditTripForm} disabled={editTripFormLoading}>
            Cancel
          </button>
          <button type="submit" class="btn-submit" disabled={editTripFormLoading}>
            {editTripFormLoading ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}

<!-- Review Form Modal (only for completed trips) -->
{#if showReviewForm && trip.bnb && isCompleted}
  <div class="modal-overlay" on:click={closeReviewForm}>
    <div class="modal-content" on:click|stopPropagation>
      <div class="modal-header">
        <h2>Add Review</h2>
        <button class="modal-close" on:click={closeReviewForm}>×</button>
      </div>
      
      <form on:submit|preventDefault={handleAddReview} class="form">
        {#if reviewFormError}
          <div class="form-error">{reviewFormError}</div>
        {/if}
        
        <div class="form-group">
          <label>Rating (1-5) *</label>
          <input type="number" min="1" max="5" bind:value={reviewFormData.rating_value} required disabled={reviewFormLoading} />
        </div>
        
        <div class="form-group">
          <label>Review Statement *</label>
          <textarea bind:value={reviewFormData.statement} required disabled={reviewFormLoading} rows="4"></textarea>
        </div>
        
        <div class="form-actions">
          <button type="button" class="btn-cancel" on:click={closeReviewForm} disabled={reviewFormLoading}>Cancel</button>
          <button type="submit" class="btn-submit" disabled={reviewFormLoading}>
            {reviewFormLoading ? 'Adding...' : 'Add Review'}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}

<style>
  .trip-detail-page {
    min-height: 100vh;
    background: #f9fafb;
    padding: 2rem 0;
  }
  
  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
  }
  
  .loading-state, .error-state {
    text-align: center;
    padding: 4rem 2rem;
  }
  
  .spinner {
    font-size: 3rem;
    margin-bottom: 1rem;
  }
  
  .btn-back {
    background: #6366f1;
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    cursor: pointer;
    font-size: 1rem;
    margin-bottom: 2rem;
    transition: background 0.2s;
  }
  
  .btn-back:hover {
    background: #4f46e5;
  }
  
  .trip-header {
    margin-bottom: 3rem;
  }
  
  .trip-hero {
    position: relative;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  }
  
  .trip-image {
    width: 100%;
    height: 400px;
    background-size: cover;
    background-position: center;
  }
  
  .trip-info {
    background: linear-gradient(to top, rgba(0,0,0,0.8), transparent);
    color: white;
    padding: 3rem 2rem 2rem;
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
  }
  
  .trip-status-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  .trip-status-badge {
    margin-bottom: 0;
  }
  
  .status-completed,
  .status-planned {
    display: inline-block;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  
  .status-completed {
    background: rgba(16, 185, 129, 0.9);
    color: white;
  }
  
  .status-planned {
    background: rgba(99, 102, 241, 0.9);
    color: white;
  }

  .trip-actions {
    display: flex;
    gap: 0.5rem;
  }

  .btn-outline-light,
  .btn-outline-danger {
    padding: 0.4rem 0.9rem;
    border-radius: 999px;
    font-size: 0.9rem;
    font-weight: 600;
    cursor: pointer;
    border-width: 1px;
    border-style: solid;
    background: transparent;
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
  }

  .btn-outline-light {
    border-color: rgba(255, 255, 255, 0.8);
    color: white;
  }

  .btn-outline-light:hover {
    background: rgba(255, 255, 255, 0.15);
  }

  .btn-outline-danger {
    border-color: rgba(248, 113, 113, 0.9);
    color: #fecaca;
  }

  .btn-outline-danger:hover {
    background: rgba(248, 113, 113, 0.2);
  }
  
  .trip-info h1 {
    margin: 0 0 1rem 0;
    font-size: 2.5rem;
  }
  
  .trip-location, .trip-date {
    margin: 0.5rem 0;
    font-size: 1.1rem;
  }

  .btn-complete {
    margin-top: 1rem;
    background: #10b981;
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 999px;
    cursor: pointer;
    font-size: 1rem;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    box-shadow: 0 10px 25px rgba(16, 185, 129, 0.4);
    transition: background 0.2s ease, transform 0.1s ease, box-shadow 0.2s ease;
  }

  .btn-complete:hover {
    background: #059669;
    transform: translateY(-1px);
    box-shadow: 0 14px 30px rgba(16, 185, 129, 0.5);
  }

  .btn-complete:active {
    transform: translateY(0);
    box-shadow: 0 6px 18px rgba(16, 185, 129, 0.4);
  }
  
  .section {
    background: white;
    border-radius: 12px;
    padding: 2rem;
    margin-bottom: 2rem;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  }
  
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
  }
  
  .section-header h2 {
    margin: 0;
    font-size: 1.5rem;
  }
  
  .btn-add {
    background: #6366f1;
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    cursor: pointer;
    font-size: 1rem;
    transition: background 0.2s;
  }
  
  .btn-add:hover {
    background: #4f46e5;
  }
  
  .plans-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
  }
  
  .plan-card {
    background: #f9fafb;
    border: 2px solid #e5e7eb;
    border-radius: 8px;
    padding: 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: start;
  }
  
  .plan-content h3 {
    margin: 0 0 0.5rem 0;
    font-size: 1.2rem;
  }
  
  .plan-content p {
    margin: 0;
    color: #6b7280;
  }
  
  .btn-delete {
    background: #ef4444;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.9rem;
  }
  
  .btn-delete:hover {
    background: #dc2626;
  }
  
  .bnb-card {
    background: #f9fafb;
    border: 2px solid #e5e7eb;
    border-radius: 8px;
    padding: 2rem;
  }
  
  .bnb-info h3 {
    margin: 0 0 1rem 0;
    font-size: 1.5rem;
  }
  
  .bnb-address, .bnb-availability, .bnb-rating {
    margin: 0.5rem 0;
    color: #374151;
  }
  
  .ratings-section, .reviews-section {
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 1px solid #e5e7eb;
  }
  
  .ratings-section h4, .reviews-section h4 {
    margin: 0 0 1rem 0;
  }
  
  .ratings-list {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
  }
  
  .rating-badge {
    background: #fef3c7;
    color: #92400e;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-weight: 600;
  }
  
  .reviews-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  
  .review-item {
    background: white;
    padding: 1rem;
    border-radius: 8px;
    border: 1px solid #e5e7eb;
  }
  
  .review-item p {
    margin: 0 0 0.5rem 0;
  }
  
  .review-item small {
    color: #6b7280;
  }
  
  .btn-add-review {
    margin-top: 1.5rem;
    background: #10b981;
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    cursor: pointer;
    font-size: 1rem;
  }
  
  .btn-add-review:hover {
    background: #059669;
  }
  
  .info-message {
    margin-top: 1.5rem;
    padding: 1rem;
    background: #fef3c7;
    border: 1px solid #fbbf24;
    border-radius: 8px;
    color: #92400e;
  }
  
  .info-message p {
    margin: 0;
    font-size: 0.95rem;
  }
  
  .empty-state {
    text-align: center;
    padding: 3rem;
    color: #6b7280;
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
  }
  
  .modal-close:hover {
    background: #f3f4f6;
  }
  
  .form {
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
  }
  
  .form-group input,
  .form-group textarea {
    width: 100%;
    padding: 12px;
    border: 2px solid #e5e7eb;
    border-radius: 8px;
    font-size: 16px;
    box-sizing: border-box;
  }
  
  .form-group input:focus,
  .form-group textarea:focus {
    outline: none;
    border-color: #6366f1;
  }
  
  .form-group input:disabled,
  .form-group textarea:disabled {
    background: #f3f4f6;
    cursor: not-allowed;
  }
  
  .form-error {
    background: #fee2e2;
    color: #dc2626;
    padding: 12px;
    border-radius: 8px;
    margin-bottom: 20px;
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
    border: none;
  }
  
  .btn-cancel {
    background: #f3f4f6;
    color: #374151;
  }
  
  .btn-submit {
    background: #6366f1;
    color: white;
  }
  
  .btn-cancel:hover:not(:disabled),
  .btn-submit:hover:not(:disabled) {
    opacity: 0.9;
  }
  
  .btn-cancel:disabled,
  .btn-submit:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
</style>

