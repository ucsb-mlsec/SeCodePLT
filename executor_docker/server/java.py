from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from .server_utils import _post_process_result, submit_poc
from .server_types import Payload

# Configuration variables (to be set from main module)
_salt = "seccodeplt-salt"
_log_dir = Path("./logs")
_docker_image = "seccodeplt/juliet-java-env"

# Java router
java_router = APIRouter(prefix="/java", tags=["java"])


def configure_java_router(salt: str, log_dir: Path, docker_image: str):
    """Configure the Java router with runtime parameters."""
    global _salt, _log_dir, _docker_image
    _salt = salt
    _log_dir = log_dir
    _docker_image = docker_image


@java_router.post("/submit-code")
def submit_java_code(
    metadata: Annotated[str, Form()],
    file: Annotated[UploadFile, File()],
):
    """Submit Java code for CWE testing"""
    try:
        payload = Payload.model_validate_json(metadata)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid metadata format") from None

    # Check if this is a Java task
    if not payload.task_id.startswith("juliet-java:"):
        raise HTTPException(
            status_code=400, detail="This endpoint is only for Java tasks"
        )

    payload.data = file.file.read()
    res = submit_poc(
        payload, mode="vul", log_dir=_log_dir, salt=_salt, image=_docker_image
    )
    res = _post_process_result(res)

    # Add Java-specific information to response
    res["language"] = "java"
    res["task_type"] = "code_completion"

    return res


@java_router.post("/submit-patch")
def submit_java_patch(
    metadata: Annotated[str, Form()],
    file: Annotated[UploadFile, File()],
):
    """Submit complete Java file for patch testing (supports both Juliet and Vul4J)"""
    try:
        payload = Payload.model_validate_json(metadata)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid metadata format") from None

    # Check task type and route to appropriate Docker container
    if payload.task_id.startswith("juliet-java:"):
        # Use Juliet Docker environment
        docker_image = _docker_image  # seccodeplt/juliet-java-env
    elif payload.task_id.startswith("vul4j:"):
        # Use official Vul4J Docker image from DockerHub
        docker_image = "bqcuongas/vul4j"
    else:
        raise HTTPException(
            status_code=400, 
            detail="Task ID must start with 'juliet-java:' or 'vul4j:'"
        )

    payload.data = file.file.read()
    res = submit_poc(
        payload, mode="patch", log_dir=_log_dir, salt=_salt, image=docker_image
    )
    res = _post_process_result(res)

    # Add task-specific information to response
    res["language"] = "java"
    res["task_type"] = "patch_generation"
    res["dataset"] = "juliet" if payload.task_id.startswith("juliet-java:") else "vul4j"

    return res