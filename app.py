from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pprint import pprint
from digest_lm.terminal_client import save_github_repo_locally
from digest_lm.inference import (
    run_inference,
    generate_instruction,
    generate_curl_scripts,
    convert_curl_script_to_python_requests,
)
import json
import logging
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

curr_action_list = [""]
list_of_responses = []  # {"timestamp": <str>, "response": <str>, "status_code": <int>}
list_of_all_responses = []
list_of_test_str = []
success_rate = 0 # in pct

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

@app.api_route("/digest-lm/success-rate", methods=["GET"])
async def digest_lm_success_rate():
    return {
        "success_rate": round(success_rate, 2)
    }


@app.api_route("/digest-lm/unit-tests", methods=["GET"])
async def digest_lm_unit_tests():
    refactored_dict = {"tests": []}

    for test_str in list_of_test_str:
        refactored_dict["tests"].append({"name": test_str, "description": test_str})

    return refactored_dict


@app.api_route("/digest-lm/requests-per-minute", methods=["GET"])
async def digest_lm_requests_per_minute():

    global list_of_all_responses

    curr_timestamp = datetime.now()

    start = curr_timestamp - timedelta(minutes=10)

    reqs_200 = 0
    reqs_error = 0

    list_of_request_summary = []

    for i in range(10):

        start = start + timedelta(minutes=1)
        tmp_dict = {
            "timestamp": start.strftime("%H:%M"),
            "HTTP_2xx": 0,
            "HTTP_error": 0
        }

        print(start)
        for response in list_of_all_responses:
            if response["timestamp"] >= start.isoformat() and response["timestamp"] < (start + timedelta(minutes=1)).isoformat():
                print(response["status_code"])
                if response["status_code"] == 200:
                    reqs_200 += 1
                    tmp_dict["HTTP_2xx"] += 1
                else:
                    reqs_error += 1
                    tmp_dict["HTTP_error"] += 1

        list_of_request_summary.append(tmp_dict)

    print(list_of_request_summary)

    print(reqs_200)
    print(reqs_error)

    # print(min_timestamp)

    return {
        "requests": list_of_request_summary
    }


@app.api_route("/digest-lm/output", methods=["GET"])
async def digest_lm_output():
    global success_rate
    print(">>>>>>>")
    print(list_of_responses)

    reqs_200 = 0

    refactored_dict = {"output": []}

    for response in list_of_responses:
        refactored_dict["output"].append(
            {
                "name": response["response"].text,
                "description": response["response"].status_code,
            }
        )
        print(response["response"].status_code)
        if response["response"].status_code == 200:
            reqs_200 += 1


    print(success_rate)

    try:

        success_rate = reqs_200 / len(list_of_responses)
        success_rate = success_rate * 100
    except ZeroDivisionError:
        success_rate = 0

    return refactored_dict


@app.api_route("/digest-lm/actions", methods=["GET"])
async def digest_lm_actions():
    return {
        "actions": [
            {"name": curr_action_list[0], "description": "Action 1 description"},
        ]
    }


@app.api_route("/digest-lm/user-message", methods=["POST"])
async def digest_lm_user_message(request: Request):
    # list_of_test_str = []
    # list_of_responses = []

    body = await request.body()
    body_str = json.loads(body.decode())
    print(body_str)
    print(type(body_str))
    print(body_str.keys())
    model_resp = generate_instruction(body_str["message"])
    pprint(model_resp)
    print(type(model_resp))
    # print(eval(model_resp))
    model_resp_dict = json.loads(model_resp)
    if len(json.loads(model_resp)["tool_choice"]) > 3:
        curr_action_list[0] = str(json.loads(model_resp)["tool_choice"])
    print(curr_action_list)
    print(model_resp_dict["tool_choice"])
    print(model_resp_dict["tool_input"])

    GITHUB_ORG = json.loads(model_resp)["tool_input"].split("/")[0]
    GITHUB_REPO_NAME = json.loads(model_resp)["tool_input"].split("/")[1]

    if model_resp_dict["tool_choice"] == "save_github_repo_locally":
        save_github_repo_locally(
            GITHUB_ORG,
            GITHUB_REPO_NAME,
        )

    elif model_resp_dict["tool_choice"] == "generate_curl_scripts":
        curl_scripts = generate_curl_scripts(
            GITHUB_ORG,
            GITHUB_REPO_NAME,
        )
        print(curl_scripts["curl_scripts"])
        for line in curl_scripts["curl_scripts"].split("\n"):
            print(line)
            if "echo" not in line:
                list_of_test_str.append(line)
                print(">>>>>>>>>>>")
                print(list_of_test_str)

    elif model_resp_dict["tool_choice"] == "run_inference":
        with open(f"scripts/sh/{GITHUB_ORG}-{GITHUB_REPO_NAME}.sh", "r") as f:
            curl_script = f.read()
            for line in curl_script.split("\n"):
                if "echo" not in line:
                    print(line)
                    resp = convert_curl_script_to_python_requests(line)
                    print("--------------------------------")
                    print(resp)

                    resp = eval(resp)
                    print("-")
                    # print(eval(resp))
                    list_of_responses.append(
                        {
                            "timestamp": datetime.now().isoformat(),
                            "response": resp,
                            "status_code": resp.status_code,
                        }
                    )
                    list_of_all_responses.append(
                        {
                            "timestamp": datetime.now().isoformat(),
                            "response": resp,
                            "status_code": resp.status_code,
                        }
                    )
                    print("--------------------------------")
        # run_inference()

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
