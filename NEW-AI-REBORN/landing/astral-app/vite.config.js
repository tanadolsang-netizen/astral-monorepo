import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: './',
  server: {
    port: 5174,
    proxy: {
      '/v1': 'http://localhost:8000',
      '/ready': 'http://localhost:8000',
    }
  }
})
