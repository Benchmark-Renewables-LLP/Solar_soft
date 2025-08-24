import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react-swc';
import path from 'path';

console.log('Proxy config:', { target: 'http://backend:8000' });
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
      },
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
});