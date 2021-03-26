from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.starlette import register_tortoise

from app.settings.db import DATABASE
from app.auth import authrouter
from fixtures.routes import fixturerouter
from app.demoroutes import demorouter
from tests.routes import testrouter


def get_app():
    app = FastAPI()     # noqa
    
    # Routes
    app.include_router(authrouter, prefix='/auth', tags=['Auth'])
    app.include_router(demorouter, prefix='/demo', tags=['Development'])
    app.include_router(testrouter, prefix='/test', tags=['Development'])
    app.include_router(fixturerouter, prefix='/fixture', tags=['Fixtures'])

    # Tortoise
    register_tortoise(
        app,
        config=DATABASE,
        generate_schemas=True,
    )

    # CORS
    origins = ['http://localhost:3000', 'http://127.0.0.1:3000']
    app.add_middleware(
        CORSMiddleware, allow_origins=origins, allow_credentials=True,
        allow_methods=["*"], allow_headers=["*"],
    )
    
    return app


app = get_app()
