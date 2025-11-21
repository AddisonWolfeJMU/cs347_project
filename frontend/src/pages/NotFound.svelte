<script>
  function goHome() {
    window.location.hash = '#home'
  }
</script>

<main class="not-found-page">
  <div class="container">
    <div class="not-found-content">
      <div class="error-code">404</div>
      <h1>Page Not Found</h1>
      <p class="error-message">
        Oops! The page you're looking for seems to have wandered off on its own adventure.
      </p>
      <p class="error-submessage">
        Don't worry, we'll help you get back on track!
      </p>
      
      <div class="action-buttons">
        <button class="btn-primary" on:click={goHome}>
          <span class="btn-icon">🏠</span>
          <span>Go Home</span>
        </button>
        <a href="#help" class="btn-secondary">
          <span class="btn-icon">❓</span>
          <span>Get Help</span>
        </a>
      </div>

      <div class="suggestions">
        <h3>Popular Pages</h3>
        <div class="suggestion-links">
          <a href="#home" class="suggestion-link">
            <span class="link-icon">🏠</span>
            <span>Home</span>
          </a>
          <a href="#bucket" class="suggestion-link">
            <span class="link-icon">📝</span>
            <span>Bucket List</span>
          </a>
          <a href="#trips" class="suggestion-link">
            <span class="link-icon">✈️</span>
            <span>My Trips</span>
          </a>
          <a href="#profile" class="suggestion-link">
            <span class="link-icon">👤</span>
            <span>Profile</span>
          </a>
        </div>
      </div>
    </div>
  </div>
</main>

<style>
  .not-found-page {
    min-height: calc(100vh - 100px);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 60px 20px;
    background: var(--bg);
  }

  .not-found-content {
    text-align: center;
    max-width: 700px;
    margin: 0 auto;
  }

  .error-code {
    font-size: 8rem;
    font-weight: 900;
    background: linear-gradient(135deg, var(--brand) 0%,rgb(255, 0, 0) 50%, var(--accent) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
    margin: 0 0 20px 0;
    text-shadow: 0 4px 20px rgba(11, 108, 255, 0.2);
  }

  h1 {
    font-size: 2.5rem;
    margin: 0 0 20px 0;
    color: var(--text);
    font-weight: 700;
  }

  .error-message {
    font-size: 1.3rem;
    color: var(--muted);
    margin: 0 0 10px 0;
    line-height: 1.6;
  }

  .error-submessage {
    font-size: 1.1rem;
    color: var(--muted);
    margin: 0 0 40px 0;
    line-height: 1.6;
  }

  .action-buttons {
    display: flex;
    gap: 20px;
    justify-content: center;
    margin: 0 0 60px 0;
    flex-wrap: wrap;
  }

  .btn-primary,
  .btn-secondary {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    padding: 15px 35px;
    border-radius: 12px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    text-decoration: none;
    border: 2px solid transparent;
  }

  .btn-primary {
    background: var(--brand);
    color: white;
    box-shadow: 0 4px 15px rgba(11, 108, 255, 0.3);
    border: none;
  }

  .btn-primary:hover {
    background: #0056b3;
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(11, 108, 255, 0.4);
  }

  .btn-secondary {
    background: var(--surface);
    color: var(--text);
    border-color: var(--border);
  }

  .btn-secondary:hover {
    border-color: var(--brand);
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  }

  .btn-icon {
    font-size: 1.2rem;
  }

  .suggestions {
    background: var(--surface);
    border: 2px solid var(--border);
    border-radius: 20px;
    padding: 40px 30px;
    margin-top: 40px;
  }

  .suggestions h3 {
    font-size: 1.5rem;
    margin: 0 0 25px 0;
    color: var(--text);
    font-weight: 700;
  }

  .suggestion-links {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 15px;
  }

  .suggestion-link {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    padding: 20px;
    background: var(--bg);
    border: 2px solid var(--border);
    border-radius: 12px;
    text-decoration: none;
    color: var(--text);
    transition: all 0.3s ease;
    font-weight: 600;
  }

  .suggestion-link:hover {
    border-color: var(--brand);
    transform: translateY(-3px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
  }

  .link-icon {
    font-size: 2rem;
  }

  /* Responsive Design */
  @media (max-width: 768px) {
    .error-code {
      font-size: 5rem;
    }

    h1 {
      font-size: 2rem;
    }

    .error-message {
      font-size: 1.1rem;
    }

    .error-submessage {
      font-size: 1rem;
    }

    .action-buttons {
      flex-direction: column;
    }

    .btn-primary,
    .btn-secondary {
      width: 100%;
      max-width: 300px;
      justify-content: center;
    }

    .suggestion-links {
      grid-template-columns: repeat(2, 1fr);
    }
  }
</style>

