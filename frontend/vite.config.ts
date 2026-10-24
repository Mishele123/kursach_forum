import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  preview: { port: 5173, strictPort: true, proxy: { "/api": { target: "http://localhost:8000", changeOrigin: true, rewrite: path => path.replace(/^\/api/, "") }, "/media": { target: "http://localhost:8000", changeOrigin: true } } },
  server: {
    port: 5173,
    strictPort: true,
    proxy: {
      '/media': { target: 'http://localhost:8000', changeOrigin: true },
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
