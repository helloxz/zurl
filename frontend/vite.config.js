import { fileURLToPath, URL } from 'node:url'

import { defineConfig, loadEnv } from 'vite'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'
import vue from '@vitejs/plugin-vue'
// import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
// 非根目录部署时设置 VITE_BASE_URL，如 /zurl/；config 中需用 loadEnv 读取，import.meta.env 在 config 加载时可能未就绪
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const raw = (env.VITE_BASE_URL || '').trim()
  const base = raw ? (raw.replace(/\/?$/, '/')) : '/'
  return {
  base,
  server: {
    host: '0.0.0.0', // 设置监听的 IP 地址，0.0.0.0 表示监听所有可用的 IP 地址
    port: 3001, // 设置监听的端口号
  },
  plugins: [
    vue(),
    AutoImport({
      resolvers: [ElementPlusResolver()],
    }),
    Components({
      resolvers: [ElementPlusResolver()],
    }),
    //vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  build: {
    // 构建产物输出到后端静态目录，便于 Docker 打包与直接运行
    outDir: '../app/templates/dist',
    emptyOutDir: true,
    rollupOptions: {
      output: {
        entryFileNames: `index.js`,
        chunkFileNames: `[name].js`, // 如果你有代码分割，可以这样命名 chunk 文件
        assetFileNames: `index.[ext]`,
      },
    },
  },
  }
})
