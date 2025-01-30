# FastAPI FatSecret API Integration

This project integrates **FastAPI** with the **FatSecret API** to fetch nutritional information for foods. It supports **OAuth 2.0 authentication**, food search, and optional filtering.

---

## 🚀 Features
- ✅ **OAuth 2.0 authentication** using client credentials.
- ✅ **Search for food items** from FatSecret's food database.
- ✅ **Filter results** by **Generic** or **Brand** food types.
- ✅ **Structured API responses** using **Pydantic models**.
- ✅ **Error handling** for API failures and authentication issues.
- ✅ **Fully documented API** with **Swagger UI**.

---

## 🔧 Installation & Setup

### **1️⃣ Clone the Repository**
```sh
git clone https://github.com/your-username/fastapi-fatsecret-api.git
cd fastapi-fatsecret-api
```

### **2️⃣ Install Dependencies**
```sh
pip install fastapi uvicorn requests python-dotenv pydantic
```

### **3️⃣ Set Up `.env` File**
Create a `.env` file and add your **FatSecret API credentials**:
```sh
FATSECRET_CLIENT_ID=your_actual_client_id
FATSECRET_CLIENT_SECRET=your_actual_client_secret
```

### **4️⃣ Run the FastAPI Server**
```sh
uvicorn app:app --host 0.0.0.0 --port 8888 --reload
```

### **5️⃣ Test the API in Swagger UI**
- Open **[http://127.0.0.1:8888/docs](http://127.0.0.1:8888/docs)** in your browser.
- Use the **Authorize** button to test authentication.
- Try the `/search_foods` endpoint.

---

## 📝 API Endpoints

### **🔍 Search Foods**
#### **`GET /search_foods`**
Searches for food items in the FatSecret database.

**📥 Request Parameters:**
| Parameter     | Type   | Description |
|--------------|--------|-------------|
| `query` (required) | `string` | Search term (e.g., `"apple"`) |
| `page_number` | `int` | Pagination offset (default: `0`) |
| `max_results` | `int` | Number of results (max: `50`) |
| `food_type` | `string` | Optional filter (`Generic` or `Brand`) |

**📤 Example Request:**
```sh
curl -X GET "http://0.0.0.0:8888/search_foods?query=apple&page_number=0&max_results=10"
```

**📥 Example Response:**
```json
{
  "total_results": 2003,
  "max_results": 10,
  "page_number": 0,
  "foods": [
    {
      "food_id": "35718",
      "food_name": "Apples",
      "food_type": "Generic",
      "brand_name": null,
      "food_description": "Per 100g - Calories: 52kcal | Fat: 0.17g | Carbs: 13.81g | Protein: 0.26g",
      "food_url": "https://www.fatsecret.com/calories-nutrition/usda/apples"
    },
    {
      "food_id": "1902657",
      "food_name": "Honeycrisp Apples",
      "food_type": "Generic",
      "brand_name": null,
      "food_description": "Per 100g - Calories: 52kcal | Fat: 0.17g | Carbs: 13.81g | Protein: 0.26g",
      "food_url": "https://www.fatsecret.com/calories-nutrition/generic/apples-honeycrisp"
    }
  ]
}
```
