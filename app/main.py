from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from app import api

app = FastAPI(
    title="FatSecret Food Search API",
    description="A small FastAPI wrapper around the FatSecret `foods.search` endpoint.",
)


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


def _as_list(food) -> list:
    """FatSecret returns a dict (not a list) when there is exactly one match."""
    if food is None:
        return []
    if isinstance(food, dict):
        return [food]
    return list(food)


@app.get("/search_foods", response_model=FoodSearchResponse)
def search_foods(
    query: str = Query(..., min_length=1, description="Food name to search for"),
    page_number: int = Query(0, ge=0, description="Zero-based page number"),
    max_results: int = Query(20, ge=1, le=50, description="Results per page (1-50)"),
    food_type: Optional[str] = Query(None, description="Filter by 'Generic' or 'Brand'"),
):
    """Search foods using the FatSecret API, optionally filtering by food type."""
    try:
        data = api.search_foods(query, page_number=page_number, max_results=max_results)
    except api.FatSecretError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    foods = [
        {
            "food_id": food["food_id"],
            "food_name": food["food_name"],
            "food_type": food["food_type"],
            "brand_name": food.get("brand_name"),
            "food_description": food["food_description"],
            "food_url": food["food_url"],
        }
        for food in _as_list(data.get("food"))
        if food_type is None or food["food_type"].lower() == food_type.lower()
    ]

    return {
        "total_results": data.get("total_results", 0),
        "max_results": data.get("max_results", max_results),
        "page_number": data.get("page_number", page_number),
        "foods": foods,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8888)
