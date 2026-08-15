import { defineConfig } from 'vitest/config'
import path from 'path'

// 仅用于 store / 纯逻辑单元测试：不渲染组件、无 JSX，故不引入
// @vitejs/plugin-react（它在 vitest 启动时注入 HMR/babel 链，Windows 下易触发
// V8 semi-space OOM）。组件渲染测试如需新增，再单独引入 jsdom + react 插件。
export default defineConfig({
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  test: {
    environment: 'node',
    include: ['src/**/*.test.ts'],
  },
})
