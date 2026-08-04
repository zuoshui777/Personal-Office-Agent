// React 应用入口
// 渲染 App 根组件，挂载到 index.html 的 #root 节点
// 负责把App组件挂载到网页


import { StrictMode } from 'react'

import { createRoot } from 'react-dom/client'

import App from './App'

import './index.css'



createRoot(
    document.getElementById('root')!
).render(

    <StrictMode>

        <App />

    </StrictMode>

)