import asyncio
from openai import AsyncOpenAI
from app.models.schemas import GenerateRequest, TestConnectionRequest, FetchModelsRequest

import httpx

async def generate_animation_stream(request: GenerateRequest):
    # Initialize OpenAI client with user's config
    client_kwargs = {
        "api_key": request.api_key.strip(),
        "http_client": httpx.AsyncClient(
            timeout=1200.0,
        )
    }
    if request.base_url:
        client_kwargs["base_url"] = _normalize_base_url(request.base_url)
        
    client = AsyncOpenAI(**client_kwargs)
    
    bilingual_text = "中英双语字幕" if request.bilingual else "中文字幕"
    
    system_prompt = f"""
你是一个专业的前端动画生成助手。请你生成一个非常精美的前端动态动画,讲讲以下主题: {request.topic}

要求：
1. 要动态的，要像一个完整的，自动播放的视频。包含完整的过程，能把知识点讲清楚。
2. 页面极为精美，好看，有设计感，能够很好的传达知识的同时，知识和图像要准确，让初学者能够理解。
3. 附带一些旁白式的文字解说，从头到尾讲清楚一个小的知识点。
4. 不需要任何互动按钮，直接开始播放。
5. 使用现代简约风格，广泛采用的浅色配色方案，使用很多的，丰富的视觉元素。{bilingual_text}。
6. 技术细节补充: {request.tech_details}
7. 请保证任何一个元素都在一个 {request.resolution} 分辨率的容器中被摆在了正确的位置，避免穿模，字幕遮挡，图形位置错误等问题影响正确的视觉传达。
8. 你的输出必须是一个完整的单个 HTML 文件的内容，包含所有的 html、css、js 和 svg。不要输出多余的解释，只要输出代码。不要包含 ```html 标记。
    """
    
    response = None
    try:
        response = await client.chat.completions.create(
            model=request.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"生成关于【{request.topic}】的技术动画。"}
            ],
            temperature=0.6,
            top_p=0.9,
            max_tokens=16384,
            stream=True
        )
        
        async for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    except asyncio.CancelledError:
        # Client disconnected / aborted — close the OpenAI stream
        if response is not None:
            await response.close()
        print("[INFO] Generation aborted by client.")
        return
    except Exception as e:
        import traceback
        traceback.print_exc()
        yield f"ERROR: Failed to generate animation: {str(e)}"

# Providers that require a /v1 path prefix for OpenAI-compatible access
_PROVIDERS_NEED_V1 = [
    "deepseek.com",
    "openai.com",
    "siliconflow.cn",
    "api2d.net",
    "openrouter.ai",
]

def _normalize_base_url(url: str) -> str:
    """Normalize the base URL for OpenAI-compatible APIs.
    """
    base_url = url.strip()
    
    # Strip trailing slashes
    base_url = base_url.rstrip("/")
    
    # Strip known trailing path segments (order matters: longest first)
    for suffix in ["/chat/completions", "/completions", "/chat"]:
        if base_url.endswith(suffix):
            base_url = base_url[:-len(suffix)]
            break
    
    # Strip trailing slashes again after suffix removal
    base_url = base_url.rstrip("/")
    
    # For known providers, ensure URL ends with /v1
    for provider in _PROVIDERS_NEED_V1:
        if provider in base_url:
            if not base_url.endswith("/v1"):
                base_url += "/v1"
            break
    
    return base_url


async def test_api_connection(request: TestConnectionRequest) -> dict:
    """Test whether the API connection is valid by listing models."""
    try:
        base_url = _normalize_base_url(request.base_url)
        
        async with httpx.AsyncClient(timeout=15.0) as http_client:
            headers = {
                "Authorization": f"Bearer {request.api_key.strip()}",
                "Content-Type": "application/json",
            }
            # Try /v1/models endpoint to validate
            models_url = f"{base_url}/models"
            resp = await http_client.get(models_url, headers=headers)
            
            if resp.status_code == 200:
                return {"success": True, "message": "连接成功！API 可用。"}
            elif resp.status_code == 401:
                return {"success": False, "message": "认证失败：API Key 无效。"}
            elif resp.status_code == 403:
                return {"success": False, "message": "权限不足：API Key 无权访问。"}
            else:
                return {"success": False, "message": f"连接失败，HTTP 状态码: {resp.status_code}"}
    except httpx.ConnectError:
        return {"success": False, "message": "连接失败：无法连接到服务器，请检查 Base URL。"}
    except httpx.TimeoutException:
        return {"success": False, "message": "连接超时：服务器无响应。"}
    except Exception as e:
        return {"success": False, "message": f"连接失败: {str(e)}"}


async def fetch_available_models(request: FetchModelsRequest) -> dict:
    """Fetch available models from the API provider."""
    try:
        base_url = _normalize_base_url(request.base_url)
        
        async with httpx.AsyncClient(timeout=15.0) as http_client:
            headers = {
                "Authorization": f"Bearer {request.api_key.strip()}",
                "Content-Type": "application/json",
            }
            models_url = f"{base_url}/models"
            resp = await http_client.get(models_url, headers=headers)
            
            if resp.status_code != 200:
                return {"models": [], "message": f"获取模型列表失败，HTTP 状态码: {resp.status_code}"}
            
            data = resp.json()
            model_ids = []
            
            # OpenAI standard format: {"data": [{"id": "model-name", ...}, ...]}
            if "data" in data and isinstance(data["data"], list):
                model_ids = sorted([m.get("id", "") for m in data["data"] if m.get("id")])
            # Some providers return a flat list
            elif isinstance(data, list):
                model_ids = sorted([m.get("id", str(m)) if isinstance(m, dict) else str(m) for m in data])
            
            if not model_ids:
                return {"models": [], "message": "API 返回了空的模型列表。"}
            
            return {"models": model_ids, "message": f"成功获取 {len(model_ids)} 个模型。"}
    
    except httpx.ConnectError:
        return {"models": [], "message": "连接失败：无法连接到服务器。"}
    except httpx.TimeoutException:
        return {"models": [], "message": "连接超时：服务器无响应。"}
    except Exception as e:
        return {"models": [], "message": f"获取模型列表失败: {str(e)}"}

