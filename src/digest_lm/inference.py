# from github import Github
# from github import Auth
# import os
# import requests
# from dotenv import load_dotenv

# load_dotenv()


# auth = Auth.Token(os.getenv("GITHUB_ACCESS_TOKEN"))
# g = Github(auth=auth)

# repo = g.get_repo("luchog01/minimalistic-fastapi-template")
# contents = repo.get_contents("")

# print(contents)

# RAW_GITHUB_CONTENT: str = ""

# contents = repo.get_contents("")
# while contents:
#     file_content = contents.pop(0)
#     if file_content.type == "dir":
#         contents.extend(repo.get_contents(file_content.path))
#     else:
#         # print(file_content)
#         print(".", end="")
#         # FILE_URL = f"https://raw.githubusercontent.com/PyGithub/PyGithub/refs/heads/main/github/ContentFile.py"
#         # FILE_URL = f"https://raw.githubusercontent.com/PyGithub/PyGithub/refs/heads/main/.git-blame-ignore-revs"
#         FILE_URL = f"https://raw.githubusercontent.com/{repo.full_name}/refs/heads/main/{file_content.path}"
#         content = requests.get(FILE_URL).text
#         # print(content)
#         # print(file_content.path)
#         # print(FILE_URL)
#         RAW_GITHUB_CONTENT += f"{file_content.path}\n{content}\n"

#         # print("--------------------------------")
#         # break




# # for file in contents:
# #     print(file.name)
# #     # print(file.decoded_content)
# #     code = repo.get_contents(file.path)
# #     # print(code.decoded_content)

# #     content = requests.get(FILE_URL).text
# #     print(content)
# #     print("--------------------------------")

# with open("raw_github_content.txt", "w") as f:
#     f.write(RAW_GITHUB_CONTENT)

from openai import OpenAI

import os
from dotenv import load_dotenv

load_dotenv()

with open("raw_github_content.txt", "r") as f:
    RAW_GITHUB_CONTENT = f.read()

client = OpenAI(
    api_key=os.environ.get("LLAMA_API_KEY"),
    base_url="https://api.llama.com/compat/v1/"
)

completion = client.chat.completions.create(
    model="Llama-4-Maverick-17B-128E-Instruct-FP8",
    messages=[
        {
          "role": "system",
          "content": f"You are a vercel instance that hosts the following code. {RAW_GITHUB_CONTENT}. The user sends the following request. What do you respond?"
        },
        {
          "role": "user",
          "content": "curl -XGET /health"
        }
    ],
)

print(completion.choices[0].message.content)

def run_inference(code: str, user_input: str) -> str:
    """
    Run inference on the code and user input.
    """
    return "Hello, world!"


"https://raw.githubusercontent.com/luchog01/minimalistic-fastapi-template/refs/heads/main/api/src/users/repository.py"
