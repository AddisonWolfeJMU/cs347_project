<script>
  import { onMount } from 'svelte'
  import '../styles/destination.css'
  
  let destination = null
  let loading = true
  
  // Sample destination data - soon we will get data to come from an API
  const destinations = {
    'new-england': {
      name: 'New England',
      image: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1200',
      price: 'From $299',
      description: 'Experience the stunning fall foliage and charming coastal towns of New England. From the rocky shores of Maine to the historic streets of Boston, discover the perfect blend of natural beauty and rich history.',
      highlights: [
        'Stunning fall foliage',
        'Historic coastal towns',
        'Fresh seafood cuisine',
        'Lighthouse tours',
        'Mountain hiking trails'
      ],
      activities: [
        { name: 'Foliage Tours', duration: '4-6 hours', price: '$89' },
        { name: 'Lighthouse Cruise', duration: '2 hours', price: '$45' },
        { name: 'Historic Walking Tour', duration: '3 hours', price: '$35' },
        { name: 'Seafood Tasting', duration: '2 hours', price: '$65' }
      ],
      bestTime: 'September - November',
      weather: 'Cool, crisp air with colorful foliage'
    },
    'aspen-colorado': {
      name: 'Aspen, Colorado',
      image: 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=1200',
      price: 'From $450',
      description: 'Discover the luxury mountain resort town of Aspen, famous for world-class skiing, upscale shopping, and breathtaking mountain views. Perfect for both adventure seekers and those looking for relaxation.',
      highlights: [
        'World-class skiing',
        'Luxury mountain resorts',
        'Art galleries and culture',
        'Fine dining scene',
        'Scenic mountain drives'
      ],
      activities: [
        { name: 'Ski Lessons', duration: 'Full day', price: '$150' },
        { name: 'Mountain Hiking', duration: '4-6 hours', price: '$75' },
        { name: 'Art Gallery Tour', duration: '2 hours', price: '$25' },
        { name: 'Fine Dining Experience', duration: '2-3 hours', price: '$120' }
      ],
      bestTime: 'December - March (skiing), June - September (summer)',
      weather: 'Mountain climate with snow in winter, mild summers'
    },
    'vermont': {
      name: 'Vermont',
      image: 'https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=1200',
      price: 'From $199',
      description: 'Explore the Green Mountain State with its rolling hills, covered bridges, and charming small towns. Vermont offers a perfect escape into nature with its pristine landscapes and local farm-to-table cuisine.',
      highlights: [
        'Covered bridges',
        'Maple syrup farms',
        'Rolling green hills',
        'Farm-to-table dining',
        'Artisan cheese tours'
      ],
      activities: [
        { name: 'Maple Syrup Tour', duration: '2 hours', price: '$25' },
        { name: 'Cheese Farm Visit', duration: '3 hours', price: '$40' },
        { name: 'Covered Bridge Tour', duration: '4 hours', price: '$55' },
        { name: 'Farm-to-Table Dinner', duration: '2 hours', price: '$85' }
      ],
      bestTime: 'May - October',
      weather: 'Mild summers, colorful autumns, snowy winters'
    },
    'bali-indonesia': {
      name: 'Bali, Indonesia',
      image: 'https://images.unsplash.com/photo-1537953773345-d172ccf13cf1?w=1200',
      price: 'From $599',
      description: 'Immerse yourself in the tropical paradise of Bali, where ancient temples meet pristine beaches. Experience the unique blend of Hindu culture, lush rice terraces, and world-class resorts.',
      highlights: [
        'Ancient Hindu temples',
        'Pristine beaches',
        'Rice terrace landscapes',
        'Traditional Balinese culture',
        'Luxury beach resorts'
      ],
      activities: [
        { name: 'Temple Tour', duration: '6 hours', price: '$45' },
        { name: 'Rice Terrace Trek', duration: '4 hours', price: '$35' },
        { name: 'Beach Yoga Session', duration: '1.5 hours', price: '$25' },
        { name: 'Traditional Cooking Class', duration: '3 hours', price: '$55' }
      ],
      bestTime: 'April - October',
      weather: 'Tropical climate with warm temperatures year-round'
    },
    'santorini-greece': {
      name: 'Santorini, Greece',
      image: 'https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=1200',
      price: 'From $799',
      description: 'Discover the iconic white-washed buildings and stunning sunsets of Santorini. This volcanic island offers breathtaking views, world-class wines, and some of the most romantic settings in the world.',
      highlights: [
        'Iconic white buildings',
        'Stunning sunsets',
        'Volcanic landscapes',
        'World-class wines',
        'Romantic cliffside views'
      ],
      activities: [
        { name: 'Sunset Sailing', duration: '4 hours', price: '$120' },
        { name: 'Wine Tasting Tour', duration: '3 hours', price: '$75' },
        { name: 'Volcano Hiking', duration: '5 hours', price: '$65' },
        { name: 'Photography Tour', duration: '3 hours', price: '$85' }
      ],
      bestTime: 'May - October',
      weather: 'Mediterranean climate with hot, dry summers'
    },
    'dubai-uae': {
      name: 'Dubai, UAE',
      image: 'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=1200',
      price: 'From $699',
      description: 'Experience the futuristic skyline and luxury lifestyle of Dubai. From the world\'s tallest building to pristine beaches, Dubai offers a unique blend of modern architecture and traditional Arabian culture.',
      highlights: [
        'Burj Khalifa views',
        'Luxury shopping malls',
        'Desert safaris',
        'Pristine beaches',
        'Traditional souks'
      ],
      activities: [
        { name: 'Burj Khalifa Visit', duration: '2 hours', price: '$95' },
        { name: 'Desert Safari', duration: '6 hours', price: '$120' },
        { name: 'Gold Souk Tour', duration: '3 hours', price: '$45' },
        { name: 'Luxury Shopping', duration: '4 hours', price: '$65' }
      ],
      bestTime: 'November - March',
      weather: 'Desert climate with hot summers, mild winters'
    },
    'swiss-alps': {
      name: 'Swiss Alps',
      image: 'https://s1.it.atcdn.net/wp-content/uploads/2015/11/shutterstock_279572969.jpg',
      price: 'From $899',
      description: 'Discover the breathtaking beauty of the Swiss Alps with their pristine snow-capped peaks, charming alpine villages, and world-class ski resorts. Experience the perfect blend of adventure and luxury in one of Europe\'s most stunning mountain ranges.',
      highlights: [
        'Snow-capped mountain peaks',
        'World-class ski resorts',
        'Charming alpine villages',
        'Scenic train journeys',
        'Luxury mountain hotels'
      ],
      activities: [
        { name: 'Skiing & Snowboarding', duration: 'Full day', price: '$120' },
        { name: 'Mountain Hiking', duration: '6-8 hours', price: '$85' },
        { name: 'Scenic Train Ride', duration: '4 hours', price: '$95' },
        { name: 'Alpine Village Tour', duration: '3 hours', price: '$65' }
      ],
      bestTime: 'December - March (winter sports), June - September (hiking)',
      weather: 'Alpine climate with cold winters and mild summers'
    },
    'iceland': {
      name: 'Iceland',
      image: 'https://cdn.britannica.com/06/171306-050-C88DD752/Aurora-borealis-peninsula-Snaefellsnes-Iceland-March-2013.jpg',
      price: 'From $599',
      description: 'Explore the land of fire and ice with its dramatic landscapes, powerful waterfalls, and otherworldly geothermal features. From the Northern Lights to the Blue Lagoon, Iceland offers unforgettable natural wonders.',
      highlights: [
        'Northern Lights viewing',
        'Geysers and hot springs',
        'Dramatic waterfalls',
        'Glacier landscapes',
        'Blue Lagoon spa'
      ],
      activities: [
        { name: 'Northern Lights Tour', duration: '3-4 hours', price: '$75' },
        { name: 'Golden Circle Tour', duration: '8 hours', price: '$120' },
        { name: 'Blue Lagoon Visit', duration: '2-3 hours', price: '$85' },
        { name: 'Glacier Hiking', duration: '4 hours', price: '$95' }
      ],
      bestTime: 'September - March (Northern Lights), June - August (midnight sun)',
      weather: 'Subarctic climate with cool summers and cold winters'
    },
    'banff-canada': {
      name: 'Banff, Canada',
      image: 'https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=1200',
      price: 'From $399',
      description: 'Experience the stunning beauty of Canada\'s first national park with its turquoise lakes, towering mountain peaks, and abundant wildlife. Banff offers world-class outdoor adventures in one of the most beautiful settings on Earth.',
      highlights: [
        'Turquoise glacial lakes',
        'Towering mountain peaks',
        'Abundant wildlife',
        'Hot springs',
        'World-class hiking trails'
      ],
      activities: [
        { name: 'Lake Louise Visit', duration: '4 hours', price: '$45' },
        { name: 'Banff Gondola Ride', duration: '2 hours', price: '$65' },
        { name: 'Wildlife Viewing Tour', duration: '3 hours', price: '$55' },
        { name: 'Hot Springs Soak', duration: '1-2 hours', price: '$25' }
      ],
      bestTime: 'June - September (hiking), December - March (skiing)',
      weather: 'Mountain climate with cool summers and cold, snowy winters'
    }
  }
  
  onMount(() => {
    // Get destination ID from URL hash
    const hash = window.location.hash
    const destinationId = hash.replace('#destination/', '')
    
    if (destinationId && destinations[destinationId]) {
      destination = destinations[destinationId]
    } else {
      // Default destination if none specified
      destination = destinations['new-england']
    }
    
    loading = false
  })
  
  function goBack() {
    window.history.back()
  }
  
  function bookNow() {
    alert(`Booking ${destination.name} - ${destination.price}`)
  }
</script>

{#if loading}
  <div class="loading">
    <div class="spinner"></div>
    <p>Loading destination...</p>
  </div>
{:else if destination}
  <main class="destination-page">
    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-content">
        <button class="back-btn" on:click={goBack}>← Back</button>
        <div class="hero-text">
          <h1>{destination.name}</h1>
          <p class="hero-price">{destination.price}</p>
          <p class="hero-description">{destination.description}</p>
        </div>
      </div>
      <div class="hero-image" style={`background-image: url('${destination.image}')`}></div>
    </section>

    <!-- Highlights Section -->
    <section class="highlights">
      <h2>What Makes It Special</h2>
      <div class="highlights-grid">
        {#each destination.highlights as highlight}
          <div class="highlight-item">
            <div class="highlight-icon">✨</div>
            <p>{highlight}</p>
          </div>
        {/each}
      </div>
    </section>

    <!-- Activities Section -->
    <section class="activities">
      <h2>Popular Activities</h2>
      <div class="activities-grid">
        {#each destination.activities as activity}
          <div class="activity-card">
            <h3>{activity.name}</h3>
            <div class="activity-details">
              <span class="duration">⏱️ {activity.duration}</span>
              <span class="price">{activity.price}</span>
            </div>
          </div>
        {/each}
      </div>
    </section>

    <!-- Travel Info Section -->
    <section class="travel-info">
      <div class="info-grid">
        <div class="info-card">
          <h3>Best Time to Visit</h3>
          <p>{destination.bestTime}</p>
        </div>
        <div class="info-card">
          <h3>Weather</h3>
          <p>{destination.weather}</p>
        </div>
      </div>
    </section>

    <!-- Booking Section -->
    <section class="booking">
      <div class="booking-card">
        <h2>Ready to Experience {destination.name}?</h2>
        <p>Book your dream vacation today and create memories that will last a lifetime.</p>
        <button class="book-btn" on:click={bookNow}>Book Now - {destination.price}</button>
      </div>
    </section>
  </main>
{/if}

<!-- Styles are imported from ../styles/destination.css -->

