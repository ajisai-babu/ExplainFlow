# ExplainFlow - AI 动画生成智能体

ExplainFlow 是一个基于 AI 的技术动画生成智能体，旨在将枯燥的知识一键转化为精美、直观的高端前端动画。它采用极其现代的亮色模式设计，支持流式输出、实时预览以及 HTML 导出。

## Docker 快速启动

clone 项目到本地

```
docker-compose up -d --build
```

## 手动启动

clone 项目到本地

### 1. 启动后端 (Backend)
```bash
cd backend
# 建议使用 uv 作为包管理器
uv venv
source .venv/bin/activate

# 安装依赖
uv pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload --port 8000
```

### 2. 启动前端 (Frontend)
```bash
cd frontend
# 安装依赖
npm install

# 启动本地开发服务器
npm run dev
```

### 使用指南
1. 前端启动后，在浏览器中打开对应地址（ `http://localhost:3000`）。
2. 在左侧面板输入你想了解的技术主题（如：`JavaScript 事件循环机制`）。
3. 填入你的大模型 API Key（支持 OpenAI 兼容格式的接口，如 DeepSeek、通义千问等，可自行修改 Base URL）。
4. 点击 **生成动画** 按钮。
5. 等待生成完成后，右侧面板将渲染生成的独立 HTML 动画页面。同时支持将单文件 HTML 导出下载。


### 测试提示词

动画主题： 冒泡排序
技术细节补充：无

动画主题： CTF PWN ROP ret2text 攻击详解
技术细节补充：画出完整的函数栈帧，展示栈溢出和ret2text时栈帧的实时变化，并画出将返回地址劫持到 execve("/bin/sh") 的过程
