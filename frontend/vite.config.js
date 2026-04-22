import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // 👈 слушаем все сетевые интерфейсы
    port: 5173,       // порт можно оставить стандартным
  },
});