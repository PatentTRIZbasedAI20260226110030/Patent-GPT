from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.api.schemas.request import PatentGenerateRequest, PatentSearchRequest

router = APIRouter(prefix="/patent")


@router.post("/generate", status_code=501)
async def generate_patent(request: PatentGenerateRequest):
    return JSONResponse(
        status_code=501,
        content={"detail": "Not implemented yet"},
    )


@router.post("/search", status_code=501)
async def search_patents(request: PatentSearchRequest):
    return JSONResponse(
        status_code=501,
        content={"detail": "Not implemented yet"},
    )
