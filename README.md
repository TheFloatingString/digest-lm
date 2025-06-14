# digest-lm

Digest code from GitHub repo, and LLM acts as a server.

## Quickstart

```bash
uv sync
set LLAMA_API_KEY="<LLAMA API KEY>"
set GITHUB_ACCESS_TOKEN="<GITHUB TOKEN>"
set GITHUB_ORG="<GITHUB ORG>"
set GITHUB_REPO_NAME="<GITHUB REPO NAME>"

# to create a local copy of the repo
uv run src/digest_lm/terminal_client.py

# to run the FastAPI app
uv run uvicorn app:app --reload --host 0.0.0.0 --port 8080
```


## Priority TODO

- [x] add success rate to frontend
- [ ] add timestamps per 15 sec to frontend with error code count (200x, 400x, 500x)
- [ ] add chart to frontend
- [ ] all of NYC pings the server
- [ ] recommend changes

## Secondary TODO

- [ ] create cards for actions
- [ ] clean up duplicate curl requests
- [ ] clean up aggreagated curl requests

## TODO

- [x] pull code from GitHub CLI
- [x] pipe code into Llama Preview
- [x] pipe user input into Llama Preview
- [x] add this to a FastAPI app
- [x] user can pull any github repo
  - [x] have argparse do it for now
- [x] generate all the get requests as shell scripts for curl requests
- [ ] find candidate repos to use
- [x] create dahsboard + unit test in cli
- [x] pipe in headers
- [x] pipe in body
- [ ] reset all global vars to empty
- [ ] add curl requests to frontend
- [ ] connect function calling tools
- [ ] remove placeholders from frontend
- [ ] frontend override env vars
- [ ] keep track of logs
- [ ] have meta prompts (i.e. the entire city is pinging the website)
- [x] dashboard for HTML/stats?
- [ ] browser based terminal?
- [ ] (maybe Golang for fun?)
- [ ] port everything to a cli (quick fix)
- [ ] do accuracy comparison between llama 4 and llama 3.1
- [ ] do integration between frontend and backend
  - [ ] pip all unit tests into the frontend