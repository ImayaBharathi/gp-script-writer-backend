from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

##### API Imports
import api.users_api
import api.scripts_api
import api.script_versions_api


##### DB Engine & Model Imports
from db_models.db_setup import engine
from db_models.models import users_db_models, scripts_db_models

#### Binding Database Engine to DB Models
users_db_models.Base.metadata.create_all(bind=engine)
scripts_db_models.Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Grease Pencil Backend Server",
    description="This swagger holds the API documentation for the Grease Pencil Backend Server",
    version="0.0.1",
    contact={
        "name": "Imaya",
        "email": "imayayogi@gmail.com",
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api.users_api.router)
app.include_router(api.scripts_api.router)
app.include_router(api.script_versions_api.router)

@app.get("/health_check", tags=["Health Check"]) #### the status check endpoint is duplicated cause most cloud service expect this under /health_check url
def status_check():
    return {"status": "grease pencil backend is running"}

@app.get("/", tags=["Health Check"])
def status_check_root():
    return {"status": "grease pencil backend is running"}