import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [svelte()],

  server: {
    host: 'localhost',
    port: 5173,
    strictPort: false,
  },

  // Django serves static files at /static/
  base: '/static/',

  build: {
    // ⬅⬅⬅ THIS IS THE IMPORTANT PART
    outDir: resolve(__dirname, '../backend/static'),

    emptyOutDir: true,  // Clears old build files before writing new ones

    assetsDir: 'assets',

    rollupOptions: {
      output: {
        assetFileNames: 'assets/[name]-[hash][extname]',
        chunkFileNames: 'assets/[name]-[hash].js',
        entryFileNames: 'assets/[name]-[hash].js',
      }
    }
  }
})
