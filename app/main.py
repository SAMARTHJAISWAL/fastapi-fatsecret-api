from fastapi import FastAPI, Depends, HTTPException, Query
import requests
import os
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List, Optional

# Load environment variables
load_dotenv()

# FatSecret API credentials
CLIENT_ID = os.getenv("FATSECRET_CLIENT_ID")
CLIENT_SECRET = os.getenv("FATSECRET_CLIENT_SECRET")
TOKEN_URL = "https://oauth.fatsecret.com/connect/token"
SEARCH_URL = "https://platform.fatsecret.com/rest/server.api"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
app = FastAPI()


class FoodItem(BaseModel):
    food_id: str
    food_name: str
    food_type: str
    brand_name: Optional[str] = None
    food_description: str
    food_url: str


class FoodSearchResponse(BaseModel):
    total_results: int
    max_results: int
    page_number: int
    foods: List[FoodItem]


def get_access_token():
    """Fetch OAuth 2.0 access token"""
    data = {"grant_type": "client_credentials"}  # No "premier" scope
    response = requests.post(TOKEN_URL, auth=(CLIENT_ID, CLIENT_SECRET), data=data)

    print("OAuth Response Status:", response.status_code)
    print("OAuth Response Body:", response.text)

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Failed to obtain access token: {response.json()}")

    return response.json()["access_token"]


@app.get("/search_foods", response_model=FoodSearchResponse)
def search_foods(
    query: str = Query(..., title="Search Query", description="Enter the food name to search"),
    page_number: int = Query(0, title="Page Number", description="Pagination offset (default: 0)"),
    max_results: int = Query(20, title="Max Results", description="Number of results (max: 50)"),
    food_type: Optional[str] = Query(None, title="Food Type", description="Filter by 'Generic' or 'Brand'"),
):
    """Search foods using FatSecret API with optional filtering."""
    
    access_token = get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "method": "foods.search",
        "format": "json",
        "search_expression": query,
        "page_number": page_number,
        "max_results": min(max_results, 50),
    }

    response = requests.get(SEARCH_URL, headers=headers, params=params)
    print("FatSecret API Response:", response.text)

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch food data")

    data = response.json()["foods"]

    # Apply food_type filter if specified
    filtered_foods = [
        {
            "food_id": food["food_id"],
            "food_name": food["food_name"],
            "food_type": food["food_type"],
            "brand_name": food.get("brand_name"),
            "food_description": food["food_description"],
            "food_url": food["food_url"],
        }
        for food in data["food"]
        if food_type is None or food["food_type"].lower() == food_type.lower()
    ]

    return {
        "total_results": data["total_results"],
        "max_results": data["max_results"],
        "page_number": data["page_number"],
        "foods": filtered_foods,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)
