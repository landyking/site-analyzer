from fastapi import APIRouter, HTTPException
from app.utils import consts


router = APIRouter(prefix="/test", tags=["Test"])


@router.get("/")
async def message():
    return {"message": consts.test_content}