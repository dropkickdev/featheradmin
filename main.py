from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware



def get_app():
    app = FastAPI()     # noqa

    # Tortoise
    # register_tortoise(
    #     app,
    #     config=DATABASE,
    #     generate_schemas=True,
    # )

    # CORS
    origins = ['*']
    app.add_middleware(
        CORSMiddleware, allow_origins=origins, allow_credentials=True,
        allow_methods=["*"], allow_headers=["*"],
    )
    
    
    return app


app = get_app()