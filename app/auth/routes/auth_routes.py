from fastapi import APIRouter

from app.auth.auth import fapiuser




authrouter = APIRouter()
authrouter.include_router(fapiuser.get_register_router())