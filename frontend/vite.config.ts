// Vite 构建配置
// 配置 React 插件、开发服务器端口、代理规则（转发 API 请求至后端）
// Vite配置文件
// 配置React插件和开发服务器


import { defineConfig } from 'vite'

import react from '@vitejs/plugin-react'


export default defineConfig({

    plugins: [

        react()

    ],


    server: {

        port: 5173,

        host: "0.0.0.0"

    }

})