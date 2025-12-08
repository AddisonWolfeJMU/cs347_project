<script>
  import { onMount } from 'svelte'
  import '../styles/destination.css'
  import { getCurrentWeather } from '../lib/api.js'
  
  let destination = null
  let loading = true
  let currentWeather = null
  let weatherLoading = false
  let weatherError = null
  
  // Map destination IDs to city names for weather API
  const destinationToCity = {
    'lisbon': 'Lisbon',
    'edinburgh': 'Edinburgh',
    'london': 'London',
    'dublin': 'Dublin',
    'paris': 'Paris',
    'tokyo': 'Tokyo',
    'hong-kong': 'Hong Kong',
    'singapore': 'Singapore',
    'dubai': 'Dubai',
    'bangkok': 'Bangkok',
    // Legacy mappings (if needed)
    'new-england': 'Boston',
    'aspen-colorado': 'Aspen',
    'vermont': 'Burlington',
    'bali-indonesia': 'Denpasar',
    'santorini-greece': 'Santorini',
    'dubai-uae': 'Dubai',
    'swiss-alps': 'Zurich',
    'iceland': 'Reykjavik',
    'banff-canada': 'Banff'
  }
  
  // loaded from json
  let destinations = {}
  let isLoadingDestinations = false

  function buildSlug(name) {
    return name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '')
  }

  function generateHighlights(description) {
    if (!description) return []
    const parts = description.split(/\.\s+/).map(s => s.trim()).filter(Boolean)
    if (parts.length) return parts.slice(0, 5)
    return description.split(',').map(s => s.trim()).slice(0, 5)
  }

  function generateActivities(name, price) {
    const base = name || 'Activity'
    const p = price || 'From $0'
    return [
      { name: `${base} Highlights Tour`, duration: '2-4 hours', price: p },
      { name: `Local Culture Experience`, duration: '2-3 hours', price: '$49' },
      { name: `Scenic Trip`, duration: '4-6 hours', price: '$79' }
    ]
  }

  async function loadDestinations() {
    isLoadingDestinations = true
    try {
      const res = await fetch('/practice_results.json', { cache: 'no-store' })
      if (!res.ok) throw new Error(`Failed to fetch: ${res.status}`)
      const payload = await res.json()
      const combined = payload.results || {}
      const items = []

      for (const region of Object.keys(combined)) {
        const list = combined[region] || []
        for (const it of list) {
          const name = it.title || it.name || ''
          if (!name) continue
          const id = buildSlug(name)
          const image = it.thumbnail || it.image || ''
          const price = it.flight_price ? `From ${it.flight_price}` : (it.extracted_flight_price ? `From $${it.extracted_flight_price}` : 'From $0')
          const description = it.description || ''
          const highlights = generateHighlights(description)
          const activities = generateActivities(name, price)
          const bestTime = it.best_time_to_visit || ''

          items.push({ id, name, image, price, description, highlights, activities, bestTime, weather: '', region })
        }
      }

      destinations = Object.fromEntries(items.map(d => [d.id, d]))
    } catch (err) {
      console.error('Error loading destinations:', err)
      destinations = {}
    } finally {
      isLoadingDestinations = false
    }
  }

  function priceToNumber(p) {
    if (!p) return 0
    try {
      const m = p.toString().match(/(\d+[\d,]*)/) 
      if (!m) return 0
      return Number(m[1].replace(/,/g, ''))
    } catch (e) {
      return 0
    }
  }

  //making graph 
  function priceChartHtml(current, allDestinations) {
    if (!current) return '<p>No data</p>'
    const rawOthers = Object.values(allDestinations).filter(d => d.id !== current.id)
    const others = rawOthers.slice(0, 4)
    const insertAt = Math.floor(others.length / 2)
    const left = others.slice(0, insertAt)
    const right = others.slice(insertAt)
    const list = [...left, current, ...right]
    const values = list.map(d => priceToNumber(d.price))
    const labels = list.map(d => d.name)

    const maxVal = Math.max(...values, 1)
    const width = 420
    const height = 180
    const padding = { top: 14, right: 16, bottom: 56, left: 60 }
    const chartW = width - padding.left - padding.right
    const chartH = height - padding.top - padding.bottom
    const barGap = 16
    const barWidth = Math.max(12, Math.floor(chartW / list.length) - 8)

    const totalBarsWidth = list.length * barWidth + (list.length - 1) * barGap
    const available = chartW
    const centeredOffset = padding.left + Math.floor((available - totalBarsWidth) / 2)
    
    const chartShift = 0
    
    const extraYOffset = 14
    const startOffset = centeredOffset - chartShift

    let bars = ''
    for (let i = 0; i < list.length; i++) {
      const val = values[i]
      const h = Math.round((val / maxVal) * (chartH - 10))
      const x = startOffset + i * (barWidth + barGap)
      const y = padding.top + extraYOffset + (chartH - h)
      const isCurrent = list[i].id === current.id
      const color = isCurrent ? '#6366f1' : '#c7c7ff'
      const label = labels[i]
      bars += `<rect x="${x}" y="${y}" width="${barWidth}" height="${h}" fill="${color}" rx="4"></rect>`
      bars += `<text x="${x + barWidth/2}" y="${y - 6}" font-size="12" fill="#111" text-anchor="middle">${val ? '$' + val : ''}</text>`
      bars += `<text x="${x + barWidth/2}" y="${padding.top + chartH + 18 + extraYOffset}" font-size="12" fill="#333" text-anchor="middle">${label}</text>`
    }

    const svg = `
      <svg width="100%" viewBox="0 0 ${width} ${height}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Price comparison chart">
        <style>
          .chart-title { font: 600 14px/1.2 system-ui, -apple-system, 'Segoe UI', Roboto; }
        </style>
        <text x="${Math.floor(width/2)}" y="16" text-anchor="middle" class="chart-title">Price (USD)</text>
        ${bars}
      </svg>
    `
    return svg
  }
  
  // Helper functions for weather
  function toFahrenheit(celsius) {
    return Math.round((celsius * 9/5) + 32)
  }
  
  function getWeatherEmoji(temp) {
    if (temp >= 30) return '🌞'
    if (temp >= 20) return '☀️'
    if (temp >= 10) return '🌤️'
    if (temp > 0) return '⛅'
    return '❄️'
  }
  
  async function fetchWeather(destinationIdOrCity, cityNameOverride) {
    // Accept either the destinationId, or a city name directly in `destinationIdOrCity`.
    let cityName = cityNameOverride || destinationToCity[destinationIdOrCity]
    if (!cityName) {
      // try to resolve from loaded destinations (use name before comma)
      const dest = destinations[destinationIdOrCity]
      if (dest && dest.name) cityName = dest.name.split(',')[0].trim()
      // if still not found, maybe the caller provided a city name directly
      if (!cityName && typeof destinationIdOrCity === 'string' && destinationIdOrCity.indexOf(' ') !== -1) {
        cityName = destinationIdOrCity
      }
    }

    if (!cityName) {
      console.warn('No city name found for weather lookup')
      // Use static fallback weather data
      setFallbackWeather(destinationIdOrCity)
      return
    }

    weatherLoading = true
    weatherError = null
    try {
      console.log(`Fetching weather for: ${cityName}`)
      const response = await getCurrentWeather(cityName)
      console.log('Weather response:', response)
      
      // API returns 'temperature' field (in Celsius)
      const tempC = response.temperature
      
      if (tempC === undefined || tempC === null) {
        throw new Error('Temperature data not available')
      }
      
      currentWeather = {
        city: response.city || cityName,
        temperature_c: tempC,
        temperature_f: toFahrenheit(tempC),
        emoji: getWeatherEmoji(tempC)
      }
      console.log('Weather set:', currentWeather)
    } catch (error) {
      console.error(`Error fetching weather for ${cityName}:`, error)
      // Use static fallback when API fails
      setFallbackWeather(destinationIdOrCity)
    } finally {
      weatherLoading = false
    }
  }

  // Static fallback weather data for when API is unavailable
  function setFallbackWeather(destinationId) {
    const fallbackWeatherData = {
      'lisbon': { temp_c: 18, emoji: '☀️' },
      'edinburgh': { temp_c: 8, emoji: '⛅' },
      'london': { temp_c: 12, emoji: '🌤️' },
      'dublin': { temp_c: 10, emoji: '🌤️' },
      'paris': { temp_c: 14, emoji: '⛅' },
      'tokyo': { temp_c: 15, emoji: '☀️' },
      'hong-kong': { temp_c: 22, emoji: '☀️' },
      'singapore': { temp_c: 28, emoji: '🌞' },
      'dubai': { temp_c: 26, emoji: '🌞' },
      'bangkok': { temp_c: 30, emoji: '🌞' }
    }

    const data = fallbackWeatherData[destinationId] || { temp_c: 20, emoji: '☀️' }
    const cityName = destinationToCity[destinationId] || 'City'
    
    currentWeather = {
      city: cityName,
      temperature_c: data.temp_c,
      temperature_f: toFahrenheit(data.temp_c),
      emoji: data.emoji
    }
    // Clear error so weather displays
    weatherError = null
  }
  
  onMount(async () => {
    await loadDestinations()

    // Get destination ID from URL hash
    const hash = window.location.hash
    const destinationId = hash.replace('#destination/', '')

    if (destinationId && destinations[destinationId]) {
      destination = destinations[destinationId]
      // Fetch weather for this destination (function will try to derive city)
      fetchWeather(destinationId)
    } else {
      // Default destination: first loaded item or new-england fallback
      const firstKey = Object.keys(destinations)[0]
      const fallback = firstKey || 'new-england'
      destination = destinations[fallback] || null
      if (destination) fetchWeather(fallback)
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
          <h3>Current Weather</h3>
          {#if weatherLoading}
            <div class="weather-loading">
              <div class="weather-spinner"></div>
              <p>Loading weather...</p>
            </div>
          {:else if currentWeather}
            <div class="current-weather-display">
              <div class="weather-emoji-large">{currentWeather.emoji}</div>
              <div class="weather-temp-display">
                <span class="temp-main">{currentWeather.temperature_f}°F</span>
                <span class="temp-sub">({currentWeather.temperature_c}°C)</span>
              </div>
              <p class="weather-location">{currentWeather.city}</p>
            </div>
          {:else if weatherError}
            <p class="weather-error-text">⛅ Weather data temporarily unavailable</p>
            <p class="weather-unavailable" style="font-size: 0.85rem; margin-top: 8px;">{weatherError}</p>
          {:else}
            <p class="weather-error-text">⛅ Loading weather information...</p>
          {/if}
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

    <!-- Price Chart Section (separate box below booking) -->
    <section class="price-chart-section">
      <div class="chart-box">
        <h3>Price comparison</h3>
        {#if destinations && Object.keys(destinations).length > 0}
          {#key destination?.id}
            {@html priceChartHtml(destination, destinations)}
          {/key}
        {:else}
          <p>No comparison data available.</p>
        {/if}
      </div>
    </section>
  </main>
{/if}

<!-- Styles are imported from ../styles/destination.css -->

