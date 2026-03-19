# ExplainFlow - AI Animation Generation Agent

ExplainFlow is an AI-powered technical animation generation agent designed to transform dry knowledge into beautiful, intuitive, high-end frontend animations with one click. It features an extremely modern light-mode design, supporting streaming output, real-time preview, and HTML export.

## Docker Quick Start

Clone the project locally:

```bash
docker-compose up -d --build
```

## Manual Start

Clone the project locally:

### 1. Start Backend
```bash
cd backend
# uv is recommended as the package manager
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt

# Start service
uvicorn app.main:app --reload --port 8000
```

### 2. Start Frontend
```bash
cd frontend
# Install dependencies
npm install

# Start local development server
npm run dev
```

### User Guide
1. Once the frontend is started, open the corresponding address in your browser (`http://localhost:3000`).
2. Enter the technical topic you want to learn about in the left panel (e.g., `JavaScript Event Loop Mechanism`).
3. Fill in your LLM API Key (supports OpenAI-compatible formats like DeepSeek, Qwen, etc.; the Base URL can be modified).
4. Click the **Generate Animation** button.
5. After generation is complete, the right panel will render the standalone HTML animation page. It also supports exporting and downloading the single-file HTML.

### Test Prompts

**Animation Topic:** Bubble Sort  
**Technical Details:** None

**Animation Topic:** CTF PWN ROP ret2text Attack Explained  
**Technical Details:** Draw a complete function stack frame, showing the real-time changes of the stack frame during stack overflow and ret2text, and illustrate the process of hijacking the return address to `execve("/bin/sh")`.
