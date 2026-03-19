from pydantic import BaseModel
from typing import Optional, List

class GenerateRequest(BaseModel):
    topic: str
    bilingual: bool = False
    tech_details: str = ""
    resolution: str = "1080p"
    api_key: str
    base_url: Optional[str] = None
    model: str = "deepseek-chat"

class GenerateResponse(BaseModel):
    html_content: str


class TestConnectionRequest(BaseModel):
    base_url: str
    api_key: str
    api_type: str = "openai-completions"

class TestConnectionResponse(BaseModel):
    success: bool
    message: str

class FetchModelsRequest(BaseModel):
    base_url: str
    api_key: str
    api_type: str = "openai-completions"
    compatible_new_api: bool = False

class FetchModelsResponse(BaseModel):
    models: List[str]
    message: str
