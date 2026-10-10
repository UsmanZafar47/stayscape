import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  // Same-origin API + images avoid browser CORS changes. Preview also supports build tests.
  server: { port: 5173, strictPort: true, proxy: { '/api': 'http://127.0.0.1:8000', '/static': 'http://127.0.0.1:8000' } },
  preview: { port: 4173, strictPort: true, proxy: { '/api': 'http://127.0.0.1:8000', '/static': 'http://127.0.0.1:8000' } },
});
