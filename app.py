from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from time import perf_counter
import uvicorn

from routes.survey_service import router as survey_router
from routes.auth_routes import router as auth_router
from utils.logger import logger, log_api_response

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


@app.middleware("http")
async def log_response_middleware(request: Request, call_next):
    start = perf_counter()
    response = await call_next(request)
    duration_ms = (perf_counter() - start) * 1000

    log_api_response(
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=duration_ms,
        query_string=request.url.query,
    )

    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    try:
        body = await request.json()
    except Exception:
        body = await request.body()

    logger.error(
        "422 validation error on %s %s | errors=%s | body=%s",
        request.method,
        request.url.path,
        exc.errors(),
        body,
    )

    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    body = None

    content_type = request.headers.get("content-type", "")

    try:
        if "application/json" in content_type:
            body = await request.json()
        else:
            body = f"<{content_type}>"
    except Exception:
        body = "<Unable to read body>"

    logger.error(
        "HTTP error on %s %s | status=%s | detail=%s | body=%s",
        request.method,
        request.url.path,
        exc.status_code,
        exc.detail,
        body,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(
        "Unhandled error on %s %s",
        request.method,
        request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
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
