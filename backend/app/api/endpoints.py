from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.models.schemas import (
    GenerateRequest, GenerateResponse,
    TestConnectionRequest, TestConnectionResponse,
    FetchModelsRequest, FetchModelsResponse,
)
from app.services.agent_service import (
    generate_animation_stream,
    test_api_connection,
    fetch_available_models,
)

router = APIRouter()

@router.post("/generate")
async def generate(request: GenerateRequest):
    return StreamingResponse(
        generate_animation_stream(request),
        media_type="text/event-stream"
    )

@router.post("/test-connection", response_model=TestConnectionResponse)
async def test_connection(request: TestConnectionRequest):
    result = await test_api_connection(request)
    return result

@router.post("/fetch-models", response_model=FetchModelsResponse)
async def fetch_models(request: FetchModelsRequest):
    result = await fetch_available_models(request)
    return result

