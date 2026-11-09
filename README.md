# FastAPI FatSecret API

[![tests](https://github.com/SAMARTHJAISWAL/fastapi-fatsecret-api/actions/workflows/tests.yml/badge.svg)](https://github.com/SAMARTHJAISWAL/fastapi-fatsecret-api/actions/workflows/tests.yml)

A small FastAPI service that wraps the [FatSecret Platform API](https://platform.fatsecret.com/) `foods.search` method. It authenticates with FatSecret using OAuth 2.0 client credentials and returns a clean, typed list of matching foods with their nutrition summary.

## Features

- OAuth 2.0 client-credentials authentication against FatSecret, with the access token cached until it expires.
- `GET /search_foods` with pagination (`page_number`, `max_results` up to 50).
- Optional filter by food type (`Generic` or `Brand`, case-insensitive).
- Pydantic response models, so the schema shows up in Swagger UI at `/docs`.
- Upstream failures (missing credentials, network errors, FatSecret error payloads such as an un-whitelisted IP) come back as HTTP 502 with a readable message.

## Tech stack

Python 3.10+, FastAPI, Pydantic v2, Uvicorn, Requests, python-dotenv, pytest.

## Setup

```sh
git clone https://github.com/SAMARTHJAISWAL/fastapi-fatsecret-api.git
cd fastapi-fatsecret-api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in your credentials
```

### Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `FATSECRET_CLIENT_ID` | yes | OAuth 2.0 client ID from your FatSecret developer account |
| `FATSECRET_CLIENT_SECRET` | yes | OAuth 2.0 client secret |
| `FATSECRET_TIMEOUT` | no | Timeout in seconds for calls to FatSecret (default `10`) |

FatSecret only accepts API calls from IP addresses you have whitelisted in the developer console. If you see `FatSecret error 21: Invalid IP address`, add your IP there.

## Run

```sh
./run.sh
# or
uvicorn app.main:app --host 0.0.0.0 --port 8888 --reload
```

Open <http://127.0.0.1:8888/docs> for the interactive Swagger UI.

## API

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/search_foods` | Search FatSecret foods |

Query parameters for `/search_foods`:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | (required) | Search term, e.g. `apple` |
| `page_number` | int | `0` | Zero-based page number |
| `max_results` | int | `20` | Results per page, 1 to 50 |
| `food_type` | string | none | Keep only `Generic` or `Brand` foods |

Note that the `food_type` filter is applied to the page FatSecret returns, so a filtered page can contain fewer than `max_results` items while `total_results` still reflects the unfiltered search.

Example:

```sh
curl "http://127.0.0.1:8888/search_foods?query=apple&max_results=2"
```

```json
{
  "total_results": 2003,
  "max_results": 2,
  "page_number": 0,
  "foods": [
    {
      "food_id": "35718",
      "food_name": "Apples",
      "food_type": "Generic",
      "brand_name": null,
      "food_description": "Per 100g - Calories: 52kcal | Fat: 0.17g | Carbs: 13.81g | Protein: 0.26g",
      "food_url": "https://www.fatsecret.com/calories-nutrition/usda/apples"
    }
  ]
}
```

## Project structure

```
app/
  config.py   # env-var configuration
  api.py      # FatSecret client: token caching + foods.search
  main.py     # FastAPI app and response models
tests/
  test_search.py
run.sh
requirements.txt / requirements-dev.txt
```

## Tests

The tests stub out the FatSecret client, so they need no network or credentials.

```sh
pip install -r requirements-dev.txt
python -m pytest
```

## Licence

[MIT](LICENSE) © 2025–2026 Samarth Jaiswal
