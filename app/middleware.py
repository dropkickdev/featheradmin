from fastapi import Request

from main import get_app


app = get_app()


# @app.middleware('http')
# async def debug_data(request: Request, call_next):
#     print(vars(request))
#     res = await call_next(request)
#     return res