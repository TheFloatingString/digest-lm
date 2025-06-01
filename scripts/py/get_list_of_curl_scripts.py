from digest_lm.inference import generate_curl_scripts
import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_ORG = os.getenv("GITHUB_ORG")
GITHUB_REPO_NAME = os.getenv("GITHUB_REPO_NAME")


def main():
    curl_scripts = generate_curl_scripts(GITHUB_ORG, GITHUB_REPO_NAME)
    for curl_script in curl_scripts["curl_scripts"].split("\n"):
        print(curl_script)
    with open(f"scripts/sh/{GITHUB_ORG}-{GITHUB_REPO_NAME}.sh", "w") as f:
        f.write(curl_scripts["curl_scripts"])


if __name__ == "__main__":
    main()
