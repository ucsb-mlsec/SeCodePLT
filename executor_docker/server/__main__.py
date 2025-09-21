import argparse
from contextlib import asynccontextmanager
from pathlib import Path

import docker
import uvicorn
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from .java import configure_java_router, java_router
from .python import python_router, set_executor_id
from .types import DEFAULT_SALT

SALT = DEFAULT_SALT
LOG_DIR = Path("./logs")
API_KEY = "secodeplt-030a0cd7-5908-4862-8ab9-91f2bfc7b56d"
API_KEY_NAME = "X-API-Key"
JAVA_DOCKER_IMAGE = "secodeplt/juliet-java-env"
PYTHON_DOCKER_IMAGE = "secodeplt/python-env"


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = docker.from_env()
    # TODO: check health of the container
    container = client.containers.run(
        image=PYTHON_DOCKER_IMAGE,
        detach=True,
    )
    set_executor_id(container.id)
    yield

    # cleanup
    container.remove(force=True)


app = FastAPI(lifespan=lifespan)

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def get_api_key(api_key: str = Security(api_key_header)):
    if api_key == API_KEY:
        return api_key
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")


public_router = APIRouter()
private_router = APIRouter(dependencies=[Depends(get_api_key)])


@public_router.get("/")
def root():
    return {
        "message": "SeCodePlt Server API",
        "version": "1.0.0",
        "endpoints": {
            "public": ["GET /", "GET /docs"],
            "java": ["POST /java/submit-code", "POST /java/submit-patch"],
            "python": ["POST /python/run_testcases"],
            "private": [],
        },
    }


app.include_router(public_router)
app.include_router(private_router)
app.include_router(java_router)
app.include_router(python_router)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SeCodePLT Server")
    parser.add_argument(
        "--host", type=str, default="127.0.0.1", help="Host to run the server on"
    )
    parser.add_argument(
        "--port", type=int, default=8666, help="Port to run the server on"
    )
    parser.add_argument("--salt", type=str, default=SALT, help="Salt for checksum")
    parser.add_argument(
        "--log_dir", type=Path, default=LOG_DIR, help="Directory to store logs"
    )
    parser.add_argument(
        "--java_image",
        type=str,
        default=JAVA_DOCKER_IMAGE,
        help="Docker image for Juliet Java tests",
    )
    parser.add_argument(
        "--python_image",
        type=str,
        default=PYTHON_DOCKER_IMAGE,
        help="Docker image for Python tests",
    )

    args = parser.parse_args()
    SALT = args.salt
    LOG_DIR = args.log_dir
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    JAVA_DOCKER_IMAGE = args.java_image
    PYTHON_DOCKER_IMAGE = args.python_image

    # Configure Java router with runtime parameters
    configure_java_router(SALT, LOG_DIR, JAVA_DOCKER_IMAGE)

    uvicorn.run(app, host=args.host, port=args.port)
