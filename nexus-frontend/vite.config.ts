import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/analyze-loan': 'http://127.0.0.1:8006',
      '/initialize-application': 'http://127.0.0.1:8006',
      '/upload-document': 'http://127.0.0.1:8006',
      '/application-documents': 'http://127.0.0.1:8006',
      '/health': 'http://127.0.0.1:8006',
      '/parse-smart-fill': 'http://127.0.0.1:8006',
      '/manual-review': 'http://127.0.0.1:8006',
      '/review-queue': 'http://127.0.0.1:8006',
    }
  }
})
