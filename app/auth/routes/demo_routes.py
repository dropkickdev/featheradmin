from fastapi import APIRouter, Response


demorouter = APIRouter()



@demorouter.get('/')
async def foo(_: Response):
    return 'foo'