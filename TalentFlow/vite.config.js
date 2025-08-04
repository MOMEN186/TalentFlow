// vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // any request to /api/... will be forwarded to Django
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        // optional: rewrite the path, but here it's 1:1 so not needed
        // rewrite: (path) => path.replace(/^\/api/, '')
      },
    },
  },
})
