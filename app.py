from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pprint import pprint
from digest_lm.inference import run_inference, generate_instruction
import json
import logging
import os

from dotenv import load_dotenv

load_dotenv()

curr_action_list = [""]


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logging.info(f"Request: {request.method} {request.url.path}")
    response = await call_next(request)
    return response


# @app.get("/")
# def read_root():
#     return {"message": "digest-lm"}


@app.api_route("/digest-lm/unit-tests", methods=["GET"])
async def digest_lm_unit_tests():
    return {
        "tests": [
            {"name": "Test 1", "description": "curl -i https://www.google.com"},
            {"name": "Test 2", "description": "curl -i https://www.google.com"},
            {"name": "Test 3", "description": "curl -i https://www.google.com"},
        ]
    }


@app.api_route("/digest-lm/requests-per-minute", methods=["GET"])
async def digest_lm_requests_per_minute():
    return {
        "requests": [
            {"name": "Request 1", "description": "Request 1 description"},
        ]
    }


@app.api_route("/digest-lm/output", methods=["GET"])
async def digest_lm_output():
    return {
        "output": [
            {"name": "Output 1", "description": "Output 1 description"},
        ]
    }


@app.api_route("/digest-lm/actions", methods=["GET"])
async def digest_lm_actions():
    return {
        "actions": [
            {"name": curr_action_list[0], "description": "Action 1 description"},
        ]
    }


@app.api_route("/digest-lm/user-message", methods=["POST"])
async def digest_lm_user_message(request: Request):
    body = await request.body()
    body_str = json.loads(body.decode())
    print(body_str)
    print(type(body_str))
    print(body_str.keys())
    model_resp = generate_instruction(body_str["message"])
    pprint(model_resp)
    print(type(model_resp))
    # print(eval(model_resp))
    if len(json.loads(model_resp)["tool_choice"]) > 3:
        curr_action_list[0] = str(json.loads(model_resp)["tool_choice"])
    print(curr_action_list)

    model_resp_dict = json.loads(model_resp)
    print(model_resp_dict)
    return {"message": model_resp_dict["assistant_message"]}


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
