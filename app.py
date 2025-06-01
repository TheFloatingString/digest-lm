from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response

from digest_lm.inference import run_inference

import logging
import os

from dotenv import load_dotenv

load_dotenv()


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

    body = await request.body()
    body_str = body.decode()  # Now it's bytes → str

    response = await run_inference(
        github_repo_name=os.getenv("GITHUB_REPO_NAME"),
        github_org=os.getenv("GITHUB_ORG"),
        endpoint=path,
        action=method,
        body=body_str,
        headers=request.headers,
    )

    response_dict = eval(response)

    # response_dict = eval(response["message"])
    # return Response(content=eeeeeeeeeeee["response"], status_code=response_dict["status_code"])
    # return JSONResponse(
    #     status_code=response_dict["status_code"], content=response_dict["response"]
    # )
    return Response(
        content=str(response_dict["response"]), status_code=response_dict["status_code"]
    )  # , status_code=str(response_dict['status_code']))
