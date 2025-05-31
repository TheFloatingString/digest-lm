from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from digest_lm.inference import run_inference

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logging.info(f"Request: {request.method} {request.url.path}")
    response = await call_next(request)
    return response


# @app.get("/")
# def read_root():
#     return {"message": "digest-lm"}


@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def catch_all(request: Request, full_path: str):
    method = request.method
    path = request.url.path
    logging.info(f"Unknown route hit: {method} {path}")

    response = run_inference(
        github_repo_name="luchog01/minimalistic-fastapi-template",
        endpoint=path,
        action=method,
    )

    response_dict = eval(response["message"])
    return JSONResponse(
        status_code=response_dict["status_code"], content=response_dict["response"]
    )
