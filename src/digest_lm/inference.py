from github import Github
from github import Auth

# import os
import requests
# from dotenv import load_dotenv

# load_dotenv()


import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


client = OpenAI(
    api_key=os.environ.get("LLAMA_API_KEY"), base_url="https://api.llama.com/compat/v1/"
)

RAW_GITHUB_CONTENT = ""

def save_github_repo_locally(github_org, github_repo_name):
    auth = Auth.Token(os.getenv("GITHUB_ACCESS_TOKEN"))
    g = Github(auth=auth)

    print(github_org)
    print(github_repo_name)

    repo = g.get_repo(f"{github_org}/{github_repo_name}")
    contents = repo.get_contents("")

    print(contents)

    RAW_GITHUB_CONTENT: str = ""

    contents = repo.get_contents("")
    while contents:
        try:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
            else:
                print(".", end="")
                FILE_URL = f"https://raw.githubusercontent.com/{github_org}/{github_repo_name}/refs/heads/{repo.default_branch}/{file_content.path}"
                print(FILE_URL)
                content = requests.get(FILE_URL).text
                RAW_GITHUB_CONTENT += f"{file_content.path}\n{content}\n"
        except Exception as e:
            print(e)
            continue

    with open(f"static/{github_org}-{github_repo_name}.txt", "w") as f:
        f.write(RAW_GITHUB_CONTENT)


def generate_instruction(user_message: str) -> str:
    completion = client.chat.completions.create(
        model="Llama-4-Maverick-17B-128E-Instruct-FP8",
        messages=[
            {
                "role": "system",
                "content": f"""You are a helpful assistant. Respond with a JSON object in the following format: {{"assistant_message": <str>, "tool_choice": <str>, "tool_input": <str>}}. Your options for tool choices are: 'generate_curl_scripts', 'generate_special_curl_scripts', 'save_github_repo_locally', 'run_inference'. If the user specifies a GitHub organization and repository, use the 'save_github_repo_locally' tool and set the tool_input='organization_name/repo_name' with the user's choice of organization and repository. Respond naturally in the assistant_message field. If the user asks for an invalid request, return empty string for tool_choice and tool_input. If the user asks for a special curl script (or if the generate curl request seems unreasonable), use the 'generate_special_curl_scripts' tool and set the tool_input='organization_name/repo_name/special_request' with the user's choice of organization, repository, and special request. Assume the GitHub repo is always available locally. If the user is insistent about a tool choice, return the tool choice. If the user asks for feedback on the code, provide itemized feedback on the code. Only return the JSON, do not return anything else. Here is the codebase: {RAW_GITHUB_CONTENT}""",
            },
            {"role": "user", "content": f"User message: {user_message}"},
        ],
    )

    return completion.choices[0].message.content


def convert_curl_script_to_python_requests(curl_script: str) -> dict:
    completion = client.chat.completions.create(
        model="Llama-4-Maverick-17B-128E-Instruct-FP8",
        messages=[
            {
                "role": "system",
                "content": f"You are a helpful assistant that can convert curl scripts to python requests. The user provides a curl script. Convert the curl script to a python requests call. No imports are needed, just the requests call.",
            },
            {"role": "user", "content": f"Curl script: {curl_script}"},
        ],
    )

    return completion.choices[0].message.content

def generate_special_curl_scripts(github_org: str, github_repo_name: str, special_request: str) -> dict:
    with open(f"static/{github_org}-{github_repo_name}.txt", "r") as f:
        RAW_GITHUB_CONTENT = f.read()

    completion = client.chat.completions.create(
        model="Llama-4-Maverick-17B-128E-Instruct-FP8",
        messages=[
            {
                "role": "system",
                "content": f"You are a helpful assistant that can generate curl scripts for a given codebase. The user provides the codebase, as well as a special request. Generate a sample curl request for each endpoint in the codebase. Respond with all the curl requests, separated by newlines. Only return the curl requests, do not return anything else. The base url is {os.getenv('BASE_URL')}. Add a -i flag to the curl requests, followed by 'echo\necho ---' between each curl request.",
            },
            {"role": "user", "content": f"Special request: {special_request}.\nCodebase: {RAW_GITHUB_CONTENT}"},
        ],
    )

    with open(f"scripts/sh/{github_org}-{github_repo_name}.sh", "w") as f:
        f.write(completion.choices[0].message.content)

    return {"curl_scripts": completion.choices[0].message.content}


def generate_curl_scripts(github_org: str, github_repo_name: str) -> dict:
    with open(f"static/{github_org}-{github_repo_name}.txt", "r") as f:
        RAW_GITHUB_CONTENT = f.read()

    completion = client.chat.completions.create(
        model="Llama-4-Maverick-17B-128E-Instruct-FP8",
        messages=[
            {
                "role": "system",
                "content": f"You are a helpful assistant that can generate curl scripts for a given codebase. The user provides the codebase. Generate a sample curl request for each endpoint in the codebase. Respond with all the curl requests, separated by newlines. Only return the curl requests, do not return anything else. The base url is {os.getenv('BASE_URL')}. Add a -i flag to the curl requests, followed by 'echo\necho ---' between each curl request.",
            },
            {"role": "user", "content": f"Codebase: {RAW_GITHUB_CONTENT}"},
        ],
    )

    with open(f"scripts/sh/{github_org}-{github_repo_name}.sh", "w") as f:
        f.write(completion.choices[0].message.content)

    return {"curl_scripts": completion.choices[0].message.content}


async def run_inference(
    github_org: str,
    github_repo_name: str,
    endpoint: str,
    action: str,
    body: str,
    headers: str,
) -> str:
    """
    Run inference on the code and user input.
    """
    with open(f"static/{github_org}-{github_repo_name}.txt", "r") as f:
        RAW_GITHUB_CONTENT = f.read()

    headers_str = " ".join([f"-H '{k}: {v}'" for k, v in headers.items()])

    completion = client.chat.completions.create(
        model="Llama-4-Maverick-17B-128E-Instruct-FP8",
        messages=[
            {
                "role": "system",
                "content": f"You are a vercel instance that hosts the following code. {RAW_GITHUB_CONTENT}. The user sends the following request. What do you respond? Respond in the following format: {{'status_code': <int>, 'response': <str>}} Only return the JSON, do not return anything else. Even if there is an error, only return the JSON.",
            },
            {
                "role": "user",
                "content": f"curl {action} {endpoint} -H '{headers}' -d '{body}'",
            },
        ],
    )

    print(f"curl {action} {endpoint} {headers_str} -d '{body}'")

    return completion.choices[0].message.content

    # return {"message": completion.choices[0].message.content}


if __name__ == "__main__":
    save_github_repo_locally(os.getenv("GITHUB_ORG"), os.getenv("GITHUB_REPO_NAME"))
