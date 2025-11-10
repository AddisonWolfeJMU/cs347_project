import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

// https://vite.dev/config/
export default defineConfig({
  plugins: [svelte()],
  server: {
    host: 'localhost',  // Use localhost to match API URL
    port: 5173,
    strictPort: false,
  },
})
