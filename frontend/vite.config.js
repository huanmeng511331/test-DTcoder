import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 开发环境将 /api 代理到本地 FastAPI 后端
// 后端地址可通过环境变量 BACKEND_ORIGIN 覆盖，默认本机 8000 端口
const backendOrigin = process.env.BACKEND_ORIGIN || 'http://localhost:8000'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: backendOrigin,
        changeOrigin: true,
      },
    },
  },
})
