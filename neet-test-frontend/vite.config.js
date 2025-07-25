import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    },
    allowedHosts: [
      'localhost',
      'zerotohero-1.onrender.com',
      'zerotohero-noqw.onrender.com'
    ]
  }
})
