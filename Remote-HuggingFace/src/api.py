import time
import logging
from typing import Any, Dict
from pydantic import BaseModel
from transformers import pipeline
from fastapi import FastAPI, HTTPException
from huggingface_hub import snapshot_download

from utils import get_downloaded_models


class InferenceRequest(BaseModel):
    task_name: str
    model_name: str
    pipeline_args: Dict[str, Any]
    input: Any


class InferenceResponse(BaseModel):
    time: float
    output: Any


class DownloadRequest(BaseModel):
    model_name: str


app = FastAPI()
available_models = get_downloaded_models()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/inference")
async def inference(request: InferenceRequest) -> InferenceResponse:
    if request.model_name not in available_models:
        logging.warning(f"Model {request.model_name} is not available!")
        raise HTTPException(status_code=400, detail="Model not available")

    try:
        pipe = pipeline(task=request.task_name,
                        model=request.model_name, **request.pipeline_args)
    except Exception as e:
        logging.warning(f"Exception during pipeline creation: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    try:
        start = time.time()
        output = pipe(request.input)
        end = time.time()
    except Exception as e:
        logging.warning(f"Exception during pipeline call: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    return InferenceResponse(output=output, time=end - start)


@app.post("/download", status_code=200)
async def download(request: DownloadRequest) -> None:
    global available_models

    if request.model_name in available_models:
        logging.warning(f"Model {request.model_name} is not available!")
        return

    try:
        _ = snapshot_download(repo_id=request.model_name)
    except Exception as e:
        logging.warning(f"Exception during model download: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    available_models = get_downloaded_models()
