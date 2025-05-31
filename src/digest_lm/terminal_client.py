from digest_lm.inference import save_github_repo_locally
import argparse
import os

from dotenv import load_dotenv
load_dotenv()

GITHUB_ORG = os.getenv("GITHUB_ORG")
GITHUB_REPO_NAME = os.getenv("GITHUB_REPO_NAME")


def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--github_org", type=str, required=True)
    # parser.add_argument("--github_repo_name", type=str, required=True)
    # args = parser.parse_args()
    save_github_repo_locally(GITHUB_ORG, GITHUB_REPO_NAME)


if __name__ == "__main__":
    main()