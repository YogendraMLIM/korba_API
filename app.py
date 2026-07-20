from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from routes.survey_service import router as survey_router
from routes.auth_routes import router as auth_router

app = FastAPI(
    title="Welcome to the Korba API, Powered by ML INFOMAP",
    description="Property Tax Survey API",
    version="1.0.0",
    root_path="/korba-services"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Home"])
def home():
    return {
        "message": "Korba Property Tax API is running"
    }


app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"]
)

app.include_router(
    survey_router,
    prefix="/survey",
    tags=["Survey"]
)


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )