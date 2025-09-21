import io
import json
import logging
import tarfile
import uuid

import docker
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

python_router = APIRouter(prefix="/python", tags=["python"])


_executor_id = None


def set_executor_id(executor_id: str):
    """Set the executor ID for Python tasks."""
    global _executor_id
    _executor_id = executor_id


class TestCodeParams(BaseModel):
    setup: str
    code: str
    testcases: str
    func_name: str
    install_requires: list[str]


class TestCodeOutput(BaseModel):
    capability: list[int]
    safety: list[int]
    runtime: float


@python_router.post("/run_testcases")
async def submit_python_code(params: TestCodeParams) -> TestCodeOutput:
    """Submit Python code for testing."""
    if _executor_id is None:
        raise HTTPException(status_code=500, detail="Executor ID not set")
    
    logger.debug(f"Running testcases with params: {params}")

    # Generate unique filenames
    task_id = str(uuid.uuid4())
    input_file = f"input_{task_id}.json"
    output_file = f"output_{task_id}.json"
    client = docker.from_env()
    container = None
    def cleanup():
        if container:
            try:
                container.exec_run(["rm", "-f", f"/tmp/{input_file}", f"/tmp/{output_file}"])
            except Exception as e:
                print(f"Error cleaning up files: {e}")
    try:
        container = client.containers.get(_executor_id)
        # 1. Create a BytesIO to hold the tar
        tar_buffer = io.BytesIO()
        with tarfile.open(fileobj=tar_buffer, mode="w") as tar:
            json_data = params.model_dump_json().encode("utf-8")
            tarinfo = tarfile.TarInfo(name=input_file)
            tarinfo.size = len(json_data)
            tar.addfile(tarinfo, io.BytesIO(json_data))
        tar_buffer.seek(0)

        # 2. Copy the JSON to the container
        container.put_archive(path="/tmp", data=tar_buffer)

        # 3. Run the test script in the container
        exec_result = container.exec_run(
            [
                "python",
                "/root/run_test.py",
                "--input_json",
                f"/tmp/{input_file}",
                "--output_json",
                f"/tmp/{output_file}",
            ]
        )

        if exec_result.exit_code != 0:
            raise HTTPException(
                status_code=500,
                detail=f"Test execution failed: {exec_result.output.decode()}",
            )

        # 4. Get the results from the container
        cat_result = container.exec_run(["cat", f"/tmp/{output_file}"])
        if cat_result.exit_code != 0:
            return None
        

        # Parse and return results
        ret = TestCodeOutput.model_validate_json(cat_result.output.decode())
        logger.debug(f"Test results: {ret}")
        return ret

    except docker.errors.NotFound:
        print(f"Container with ID {_executor_id} not found")
        raise HTTPException(status_code=404, detail="Container not found")
    except json.JSONDecodeError:
        print("Failed to decode JSON response from container")
        raise HTTPException(status_code=500, detail="Invalid response format")
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"Execution error: {str(e)}")
    finally:
        cleanup()
