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
  // Set base path for production build to match Django's static file serving
  base: '/static/',
  build: {
    assetsDir: 'assets',
    // Ensure assets are referenced correctly for Django
    rollupOptions: {
      output: {
        // Keep asset paths relative to base
        assetFileNames: 'assets/[name]-[hash][extname]',
      }
    }
  }
})
