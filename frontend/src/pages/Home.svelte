<script>
  import logo from '../assets/PinpointLogo.png'
  export let query = ''
  export let popular = []
  export let search
  const onEnter = (e) => { if (e.key === 'Enter') search?.() }
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

  <section class="popular container">
    <h2>POPULAR LOCATIONS</h2>
    <div class="grid">
      {#each popular as place}
        <article class="card">
          <div class="thumb" style={`background-image:url('${place.image}')`} />
          <h3>{place.title}</h3>
        </article>
      {/each}
    </div>
  </section>
</main>


