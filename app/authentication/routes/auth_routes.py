from fastapi import APIRouter

from app.authentication.authentication import fapiuser




authrouter = APIRouter()
authrouter.include_router(fapiuser.get_register_router())