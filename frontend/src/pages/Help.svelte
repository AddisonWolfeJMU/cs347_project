<script>
  import ChatWidget from '../components/ChatWidget.svelte'
  
  // FAQ sections
  const faqs = [
    {
      category: "Getting Started",
      questions: [
        {
          q: "How do I create a bucket list item?",
          a: "Navigate to the Bucket List page and click the 'Add New Item' button. Fill in the details like destination, description, category, and priority, then save your item to start planning your adventure!"
        },
        {
          q: "What categories are available?",
          a: "You can categorize your bucket list items into: Beaches, Cities, Mountains, Adventure, and Romantic experiences. This helps you organize your travel goals."
        },
        {
          q: "How do I set priority levels?",
          a: "When creating or editing a bucket list item, you can set it as High, Medium, or Low priority. This helps you focus on what matters most to you."
        }
      ]
    },
    {
      category: "Using the Bucket List",
      questions: [
        {
          q: "How do I mark an item as completed?",
          a: "Click on the circular button that appears when you hover over an item's image. You can also update items to add a completion date and move them to your completed trips."
        },
        {
          q: "Can I search and filter my bucket list?",
          a: "Yes! Use the search bar to find items by title or description, and click category filters (Beaches, Cities, etc.) to narrow down your list by interest."
        },
        {
          q: "How do I sort my bucket list?",
          a: "Use the sort dropdown to organize by Date Added, Priority, Title, or Category. This makes it easy to find what you're looking for."
        }
      ]
    },
    {
      category: "My Trips",
      questions: [
        {
          q: "How do items appear in My Trips?",
          a: "Completed items automatically appear in your My Trips page, sorted by completion date so you can see your most recent adventures first."
        },
        {
          q: "Can I see statistics about my travels?",
          a: "Yes! The My Trips page shows your total trips completed and breaks them down by category so you can see your travel patterns."
        }
      ]
    },
    {
      category: "Account & Settings",
      questions: [
        {
          q: "How do I update my profile?",
          a: "Go to the Profile page to add information about yourself, upload a profile picture, and update your preferences."
        },
        {
          q: "Can I export my bucket list?",
          a: "This feature is coming soon! Soon you'll be able to download your bucket list as a PDF or share it with friends."
        }
      ]
    }
  ]

  const contactOptions = [
    {
      icon: "📧",
      title: "Email Support",
      description: "Send us an email and we'll get back to you within 24 hours",
      action: "support@pinpoint.com"
    },
    {
      icon: "💬",
      title: "Live Chat",
      description: "Chat with our AI assistant powered by free LLM technology",
      action: "Chat Now"
    }
  ]

  const howToUseSteps = [
    {
      icon: "1️⃣",
      title: "Explore Destinations",
      description: "Visit the Home page to browse featured destinations and get inspired for your next adventure. Click on any destination to view details and add it to your bucket list."
    },
    {
      icon: "2️⃣",
      title: "Build Your Bucket List",
      description: "Go to the Bucket List page to see all your travel dreams. Use the search bar and category filters to organize by Beaches, Cities, Mountains, Adventure, or Romantic destinations."
    },
    {
      icon: "3️⃣",
      title: "Mark as Complete",
      description: "When you complete a trip, hover over the item image and click the circular button to mark it as complete. It will automatically move to your My Trips page."
    },
    {
      icon: "4️⃣",
      title: "View Your Adventures",
      description: "Check the My Trips page to see all your completed journeys, sorted by date with statistics showing your travel patterns and favorite categories."
    }
  ]

  let openQuestion = null

  function toggleQuestion(categoryIndex, questionIndex) {
    const key = `${categoryIndex}-${questionIndex}`
    openQuestion = openQuestion === key ? null : key
  }
</script>

<main class="help-page">
  <!-- Hero Section -->
  <section class="hero">
    <div class="container">
      <div class="hero-content">
        <h1>Help & Support</h1>
        <p>Get answers to common questions and learn how to make the most of PINPOINT</p>
      </div>
    </div>
  </section>

  

  <!-- How to Use Section -->
  <section class="how-to-use">
    <div class="container">
      <h2>How to Use PINPOINT</h2>
      <p class="how-to-intro">A simple guide to get started with your travel planning journey</p>
      
      <div class="steps">
        {#each howToUseSteps as step}
          <div class="step-item">
            <div class="step-icon">{step.icon}</div>
            <div class="step-content">
              <h3>{step.title}</h3>
              <p>{step.description}</p>
            </div>
          </div>
        {/each}
      </div>
    </div>
  </section>

  <!-- FAQ Section -->
  <section class="faq-section">
    <div class="container">
      <h2>Frequently Asked Questions</h2>
      <p class="faq-intro">Find quick answers to the most common questions about using PINPOINT</p>
      
      {#each faqs as category, categoryIndex}
        <div class="faq-category">
          <h3 class="category-title">
            <span class="category-emoji">{category.category === 'Getting Started' ? '🚀' : category.category === 'Using the Bucket List' ? '📝' : category.category === 'My Trips' ? '✈️' : '⚙️'}</span>
            {category.category}
          </h3>
          
          <div class="questions">
            {#each category.questions as question, questionIndex}
              {@const key = `${categoryIndex}-${questionIndex}`}
              <div class="question-item">
                <button 
                  class="question-btn {openQuestion === key ? 'open' : ''}"
                  on:click={() => toggleQuestion(categoryIndex, questionIndex)}
                >
                  <span class="question-text">{question.q}</span>
                  <span class="question-icon">{openQuestion === key ? '−' : '+'}</span>
                </button>
                {#if openQuestion === key}
                  <div class="answer">
                    <p>{question.a}</p>
                  </div>
                {/if}
              </div>
            {/each}
          </div>
        </div>
      {/each}
    </div>
  </section>

  <!-- Additional Help -->
  <section class="additional-help">
    <div class="container">
      <div class="help-content">
        <h2>Still Need Help?</h2>
        <p>Can't find what you're looking for? We're here to help you make the most of your travel planning journey.</p>
        <div class="help-buttons">
          <button class="help-btn primary">Contact Support</button>
          <button class="help-btn secondary">View Tutorials</button>
        </div>
      </div>
    </div>
  </section>
</main>

<!-- Chat Widget -->
<ChatWidget />

<style>
  .help-page {
    min-height: 100vh;
    background: var(--bg);
  }

  /* Hero Section */
  .hero {
    background: linear-gradient(135deg, var(--brand) 0%, #0056b3 50%, var(--accent) 100%);
    padding: 80px 0 60px;
    text-align: center;
    color: white;
    position: relative;
    overflow: hidden;
  }

  .hero-content h1 {
    font-size: 3.5rem;
    margin: 0 0 20px 0;
    font-weight: 800;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
  }

  .hero-content p {
    font-size: 1.3rem;
    margin: 0;
    opacity: 0.9;
    font-weight: 500;
  }

  /* Quick Actions */
  .quick-actions {
    padding: 60px 0;
    background: var(--surface);
  }

  .quick-actions h2 {
    text-align: center;
    font-size: 2.5rem;
    margin: 0 0 40px 0;
    color: var(--text);
    font-weight: 700;
  }

  .action-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 30px;
    max-width: 1000px;
    margin: 0 auto;
  }

  .action-card {
    background: var(--bg);
    border: 2px solid var(--border);
    border-radius: 20px;
    padding: 40px 30px;
    text-align: center;
    transition: all 0.3s ease;
  }

  .action-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    border-color: var(--brand);
  }

  .action-icon {
    font-size: 3rem;
    margin-bottom: 20px;
  }

  .action-card h3 {
    font-size: 1.5rem;
    margin: 0 0 15px 0;
    color: var(--text);
    font-weight: 700;
  }

  .action-card p {
    color: var(--muted);
    margin: 0 0 20px 0;
    line-height: 1.6;
  }

  .action-link {
    color: var(--brand);
    font-weight: 600;
    font-size: 1.1rem;
  }

  /* How to Use Section */
  .how-to-use {
    padding: 80px 0;
    background: var(--bg);
  }

  .how-to-use h2 {
    text-align: center;
    font-size: 2.5rem;
    margin: 0 0 15px 0;
    color: var(--text);
    font-weight: 700;
  }

  .how-to-intro {
    text-align: center;
    color: var(--muted);
    font-size: 1.1rem;
    margin: 0 0 50px 0;
  }

  .steps {
    max-width: 900px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 25px;
  }

  .step-item {
    display: flex;
    align-items: flex-start;
    gap: 25px;
    background: var(--surface);
    border: 2px solid var(--border);
    border-radius: 20px;
    padding: 30px;
    transition: all 0.3s ease;
  }

  .step-item:hover {
    transform: translateX(5px);
    border-color: var(--brand);
    box-shadow: 0 5px 20px rgba(0,0,0,0.1);
  }

  .step-icon {
    font-size: 3rem;
    flex-shrink: 0;
  }

  .step-content {
    flex: 1;
  }

  .step-content h3 {
    font-size: 1.5rem;
    margin: 0 0 10px 0;
    color: var(--text);
    font-weight: 700;
  }

  .step-content p {
    color: var(--muted);
    line-height: 1.8;
    margin: 0;
    font-size: 1.05rem;
  }

  /* FAQ Section */
  .faq-section {
    padding: 80px 0;
    background: var(--bg);
  }

  .faq-section h2 {
    text-align: center;
    font-size: 2.5rem;
    margin: 0 0 15px 0;
    color: var(--text);
    font-weight: 700;
  }

  .faq-intro {
    text-align: center;
    color: var(--muted);
    font-size: 1.1rem;
    margin: 0 0 50px 0;
  }

  .faq-category {
    max-width: 900px;
    margin: 0 auto 40px;
  }

  .category-title {
    display: flex;
    align-items: center;
    gap: 15px;
    font-size: 1.8rem;
    margin: 0 0 25px 0;
    color: var(--text);
    font-weight: 700;
    padding-bottom: 15px;
    border-bottom: 2px solid var(--border);
  }

  .category-emoji {
    font-size: 2rem;
  }

  .questions {
    display: flex;
    flex-direction: column;
    gap: 15px;
  }

  .question-item {
    background: var(--surface);
    border: 2px solid var(--border);
    border-radius: 15px;
    overflow: hidden;
    transition: all 0.3s ease;
  }

  .question-item:hover {
    border-color: var(--brand);
  }

  .question-btn {
    width: 100%;
    padding: 25px 30px;
    background: transparent;
    border: none;
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
    text-align: left;
    transition: all 0.3s ease;
  }

  .question-btn:hover {
    background: var(--bg);
  }

  .question-text {
    font-size: 1.2rem;
    font-weight: 600;
    color: var(--text);
    flex: 1;
  }

  .question-icon {
    font-size: 1.5rem;
    font-weight: bold;
    color: var(--brand);
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background: rgba(11, 108, 255, 0.1);
    transition: all 0.3s ease;
  }

  .question-btn.open .question-icon {
    background: var(--brand);
    color: white;
    transform: rotate(180deg);
  }

  .answer {
    padding: 0 30px 25px;
    animation: slideDown 0.3s ease;
  }

  @keyframes slideDown {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .answer p {
    color: var(--muted);
    line-height: 1.8;
    margin: 0;
    font-size: 1.05rem;
  }

  /* Additional Help */
  .additional-help {
    padding: 80px 0;
    background: linear-gradient(135deg, var(--surface) 0%, var(--bg) 100%);
    border-top: 1px solid var(--border);
  }

  .help-content {
    text-align: center;
    max-width: 700px;
    margin: 0 auto;
  }

  .help-content h2 {
    font-size: 2.5rem;
    margin: 0 0 20px 0;
    color: var(--text);
    font-weight: 700;
  }

  .help-content p {
    font-size: 1.2rem;
    color: var(--muted);
    margin: 0 0 40px 0;
    line-height: 1.6;
  }

  .help-buttons {
    display: flex;
    gap: 20px;
    justify-content: center;
    flex-wrap: wrap;
  }

  .help-btn {
    padding: 15px 40px;
    border-radius: 12px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    border: 2px solid transparent;
  }

  .help-btn.primary {
    background: var(--brand);
    color: white;
    box-shadow: 0 4px 15px rgba(11, 108, 255, 0.3);
  }

  .help-btn.primary:hover {
    background: #0056b3;
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(11, 108, 255, 0.4);
  }

  .help-btn.secondary {
    background: var(--surface);
    color: var(--text);
    border-color: var(--border);
  }

  .help-btn.secondary:hover {
    border-color: var(--brand);
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  }

  /* Responsive Design */
  @media (max-width: 768px) {
    .hero-content h1 {
      font-size: 2.5rem;
    }

    .hero-content p {
      font-size: 1.1rem;
    }

    .action-cards {
      grid-template-columns: 1fr;
    }

    .faq-section h2,
    .quick-actions h2,
    .how-to-use h2,
    .help-content h2 {
      font-size: 2rem;
    }

    .step-item {
      flex-direction: column;
      text-align: center;
      gap: 15px;
    }

    .step-icon {
      font-size: 2.5rem;
    }

    .category-title {
      font-size: 1.5rem;
    }

    .question-text {
      font-size: 1.1rem;
    }

    .help-buttons {
      flex-direction: column;
    }

    .help-btn {
      width: 100%;
      max-width: 300px;
    }
  }
</style>

