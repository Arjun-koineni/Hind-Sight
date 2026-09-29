import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/request': 'http://127.0.0.1:5000',
      '/outcome': 'http://127.0.0.1:5000',
      '/feedback': 'http://127.0.0.1:5000',
      '/insights': 'http://127.0.0.1:5000',
      '/health': 'http://127.0.0.1:5000',
    }
  }
})
