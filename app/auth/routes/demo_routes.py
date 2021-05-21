from fastapi import APIRouter, Response

from app import settings as s

demorouter = APIRouter()



@demorouter.get('/')
async def foo(_: Response):
    return s.TESTDATA