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


def save_github_repo_locally(github_org, github_repo_name):
    auth = Auth.Token(os.getenv("GITHUB_ACCESS_TOKEN"))
    g = Github(auth=auth)

    repo = g.get_repo(f"{github_org}/{github_repo_name}")
    contents = repo.get_contents("")

    print(contents)

    RAW_GITHUB_CONTENT: str = ""

    contents = repo.get_contents("")
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        else:
            print(".", end="")
            FILE_URL = f"https://raw.githubusercontent.com/{github_org}/{github_repo_name}/refs/heads/{repo.default_branch}/{file_content.path}"
            print(FILE_URL)
            content = requests.get(FILE_URL).text
            RAW_GITHUB_CONTENT += f"{file_content.path}\n{content}\n"

    with open(f"static/{github_org}-{github_repo_name}.txt", "w") as f:
        f.write(RAW_GITHUB_CONTENT)


def generate_curl_scripts(github_org: str, github_repo_name: str) -> dict:
    with open(f"static/{github_org}-{github_repo_name}.txt", "r") as f:
        RAW_GITHUB_CONTENT = f.read()

    completion = client.chat.completions.create(
        model="Llama-4-Maverick-17B-128E-Instruct-FP8",
        messages=[
            {"role": "system", "content": f"You are a helpful assistant that can generate curl scripts for a given codebase. The user provides the codebase. Generate a sample curl request for each endpoint in the codebase. Respond with all the curl requests, separated by newlines. Only return the curl requests, do not return anything else. The base url is {os.getenv('BASE_URL')}"},
            {"role": "user", "content": f"Codebase: {RAW_GITHUB_CONTENT}"},
        ],
    )

    return {"curl_scripts": completion.choices[0].message.content}


def run_inference(
    github_org: str, github_repo_name: str, endpoint: str, action: str
) -> str:
    """
    Run inference on the code and user input.
    """
    with open(f"static/{github_org}-{github_repo_name}.txt", "r") as f:
        RAW_GITHUB_CONTENT = f.read()

    completion = client.chat.completions.create(
        model="Llama-4-Maverick-17B-128E-Instruct-FP8",
        messages=[
            {
                "role": "system",
                "content": f"You are a vercel instance that hosts the following code. {RAW_GITHUB_CONTENT}. The user sends the following request. What do you respond? Respond in the following JSON format: {{'status_code': <int>, 'response': <str>}} Only return the JSON, do not return anything else.",
            },
            {"role": "user", "content": f"curl {action} {endpoint}"},
        ],
    )

    return completion.choices[0].message.content

    # return {"message": completion.choices[0].message.content}


if __name__ == "__main__":
    save_github_repo_locally("luchog01", "minimalistic-fastapi-template")
