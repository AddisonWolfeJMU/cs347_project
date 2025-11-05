<script>
  import { onMount } from 'svelte'
  
  let isOpen = false
  let messages = []
  let currentMessage = ''
  let isLoading = false
  let chatContainer
  
  // Initialize with welcome message
  onMount(() => {
    messages = [
      {
        id: 1,
        text: "Hi! I'm your PINPOINT travel assistant. I can help you with questions about using the website, travel planning tips, or general travel advice. How can I help you today?",
        sender: 'ai',
        timestamp: new Date()
      }
    ]
  })
  
  function toggleChat() {
    isOpen = !isOpen
  }
  
  async function sendMessage() {
    if (!currentMessage.trim() || isLoading) return
    
    const userMessage = {
      id: Date.now(),
      text: currentMessage,
      sender: 'user',
      timestamp: new Date()
    }
    
    messages = [...messages, userMessage]
    currentMessage = ''
    isLoading = true
    
    // Simulate AI response (replace with actual API call)
    setTimeout(() => {
      const aiResponse = generateAIResponse(userMessage.text)
      const aiMessage = {
        id: Date.now() + 1,
        text: aiResponse,
        sender: 'ai',
        timestamp: new Date()
      }
      messages = [...messages, aiMessage]
      isLoading = false
      
      // Scroll to bottom
      setTimeout(() => {
        if (chatContainer) {
          chatContainer.scrollTop = chatContainer.scrollHeight
        }
      }, 100)
    }, 1000)
  }
  
  function generateAIResponse(userInput) {
    const input = userInput.toLowerCase()
    
    // Travel-related responses
    if (input.includes('bucket list') || input.includes('add') || input.includes('destination')) {
      return "To add items to your bucket list, go to the Bucket List page and click 'Add New Item'. You can categorize destinations by Beaches, Cities, Mountains, Adventure, or Romantic experiences. Set priority levels to help organize your travel goals!"
    }
    
    if (input.includes('complete') || input.includes('finished') || input.includes('done')) {
      return "To mark a trip as complete, hover over the item's image and click the circular button. Completed trips automatically move to your My Trips page where you can see all your travel achievements!"
    }
    
    if (input.includes('search') || input.includes('filter') || input.includes('find')) {
      return "Use the search bar on the Bucket List page to find items by title or description. You can also click category filters (Beaches, Cities, etc.) to narrow down your list by interest."
    }
    
    if (input.includes('profile') || input.includes('account') || input.includes('settings')) {
      return "Visit the Profile page to update your information, add a profile picture, and customize your preferences. This helps personalize your PINPOINT experience!"
    }
    
    if (input.includes('travel') || input.includes('trip') || input.includes('vacation')) {
      return "PINPOINT is perfect for planning your travel adventures! Start by exploring destinations on the Home page, add them to your bucket list, and track your completed trips. What kind of travel experience are you looking for?"
    }
    
    if (input.includes('help') || input.includes('how') || input.includes('what')) {
      return "I'm here to help! You can ask me about using PINPOINT features, travel planning tips, or general questions. Try asking about bucket lists, completed trips, or how to organize your travel goals."
    }
    
    // Default responses
    const defaultResponses = [
      "That's a great question! PINPOINT helps you organize and track your travel dreams. You can create bucket lists, mark trips as complete, and see your travel statistics. What would you like to know more about?",
      "I'd be happy to help you with that! PINPOINT offers features like bucket list management, trip tracking, and travel organization. Feel free to ask me about any specific feature you'd like to learn about.",
      "Thanks for your question! PINPOINT is designed to make travel planning fun and organized. You can explore destinations, build your bucket list, and celebrate completed adventures. How can I assist you further?"
    ]
    
    return defaultResponses[Math.floor(Math.random() * defaultResponses.length)]
  }
  
  function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      sendMessage()
    }
  }
  
  function formatTime(date) {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }
</script>

<!-- Chat Widget -->
<div class="chat-widget">
  <!-- Chat Button -->
  <button class="chat-toggle" on:click={toggleChat} class:open={isOpen}>
    <span class="chat-icon">💬</span>
    <span class="chat-text">AI Assistant</span>
    {#if !isOpen}
      <span class="chat-badge">New</span>
    {/if}
  </button>
  
  <!-- Chat Window -->
  {#if isOpen}
    <div class="chat-window">
      <div class="chat-header">
        <div class="chat-title">
          <span class="chat-avatar">🤖</span>
          <div class="chat-info">
            <h3>PINPOINT Assistant</h3>
            <span class="chat-status">Online</span>
          </div>
        </div>
        <button class="chat-close" on:click={toggleChat}>×</button>
      </div>
      
      <div class="chat-messages" bind:this={chatContainer}>
        {#each messages as message}
          <div class="message {message.sender}">
            <div class="message-content">
              <div class="message-text">{message.text}</div>
              <div class="message-time">{formatTime(message.timestamp)}</div>
            </div>
          </div>
        {/each}
        
        {#if isLoading}
          <div class="message ai">
            <div class="message-content">
              <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        {/if}
      </div>
      
      <div class="chat-input">
        <input 
          type="text" 
          bind:value={currentMessage}
          placeholder="Type your message..."
          on:keypress={handleKeyPress}
          disabled={isLoading}
        />
        <button class="send-btn" on:click={sendMessage} disabled={isLoading || !currentMessage.trim()}>
          <span class="send-icon">📤</span>
        </button>
      </div>
    </div>
  {/if}
</div>

<style>
  .chat-widget {
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 1000;
  }
  
  .chat-toggle {
    background: var(--brand);
    color: white;
    border: none;
    border-radius: 50px;
    padding: 15px 20px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 1rem;
    font-weight: 600;
    box-shadow: 0 4px 20px rgba(11, 108, 255, 0.3);
    transition: all 0.3s ease;
    position: relative;
  }
  
  .chat-toggle:hover {
    background: #0056b3;
    transform: translateY(-2px);
    box-shadow: 0 6px 25px rgba(11, 108, 255, 0.4);
  }
  
  .chat-icon {
    font-size: 1.2rem;
  }
  
  .chat-badge {
    position: absolute;
    top: -5px;
    right: -5px;
    background: #ef4444;
    color: white;
    border-radius: 10px;
    padding: 2px 6px;
    font-size: 0.7rem;
    font-weight: 700;
    animation: pulse 2s infinite;
  }
  
  @keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.1); }
  }
  
  .chat-window {
    position: absolute;
    bottom: 80px;
    right: 0;
    width: 350px;
    height: 500px;
    background: var(--surface);
    border: 2px solid var(--border);
    border-radius: 20px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  
  .chat-header {
    background: var(--brand);
    color: white;
    padding: 15px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .chat-title {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  
  .chat-avatar {
    font-size: 1.5rem;
  }
  
  .chat-info h3 {
    margin: 0;
    font-size: 1.1rem;
    font-weight: 700;
  }
  
  .chat-status {
    font-size: 0.8rem;
    opacity: 0.9;
  }
  
  .chat-close {
    background: none;
    border: none;
    color: white;
    font-size: 1.5rem;
    cursor: pointer;
    padding: 5px;
    border-radius: 50%;
    transition: background 0.3s ease;
  }
  
  .chat-close:hover {
    background: rgba(255,255,255,0.2);
  }
  
  .chat-messages {
    flex: 1;
    padding: 20px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 15px;
  }
  
  .message {
    display: flex;
    margin-bottom: 10px;
  }
  
  .message.user {
    justify-content: flex-end;
  }
  
  .message.ai {
    justify-content: flex-start;
  }
  
  .message-content {
    max-width: 80%;
    padding: 12px 16px;
    border-radius: 18px;
    position: relative;
  }
  
  .message.user .message-content {
    background: var(--brand);
    color: white;
    border-bottom-right-radius: 5px;
  }
  
  .message.ai .message-content {
    background: var(--bg);
    color: var(--text);
    border: 1px solid var(--border);
    border-bottom-left-radius: 5px;
  }
  
  .message-text {
    margin-bottom: 5px;
    line-height: 1.4;
  }
  
  .message-time {
    font-size: 0.7rem;
    opacity: 0.7;
  }
  
  .typing-indicator {
    display: flex;
    gap: 4px;
    align-items: center;
  }
  
  .typing-indicator span {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--muted);
    animation: typing 1.4s infinite ease-in-out;
  }
  
  .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
  .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
  
  @keyframes typing {
    0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
    40% { transform: scale(1); opacity: 1; }
  }
  
  .chat-input {
    padding: 15px 20px;
    border-top: 1px solid var(--border);
    display: flex;
    gap: 10px;
    align-items: center;
  }
  
  .chat-input input {
    flex: 1;
    padding: 12px 16px;
    border: 2px solid var(--border);
    border-radius: 25px;
    background: var(--bg);
    color: var(--text);
    font-size: 0.9rem;
    outline: none;
    transition: border-color 0.3s ease;
  }
  
  .chat-input input:focus {
    border-color: var(--brand);
  }
  
  .chat-input input:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  .send-btn {
    background: var(--brand);
    color: white;
    border: none;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
  }
  
  .send-btn:hover:not(:disabled) {
    background: #0056b3;
    transform: scale(1.05);
  }
  
  .send-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .send-icon {
    font-size: 1rem;
  }
  
  /* Responsive Design */
  @media (max-width: 768px) {
    .chat-widget {
      bottom: 15px;
      right: 15px;
    }
    
    .chat-window {
      width: 320px;
      height: 450px;
    }
    
    .chat-toggle {
      padding: 12px 16px;
      font-size: 0.9rem;
    }
  }
  
  @media (max-width: 480px) {
    .chat-window {
      width: calc(100vw - 30px);
      right: -10px;
    }
  }
</style>

