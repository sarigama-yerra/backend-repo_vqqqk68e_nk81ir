import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Product, ProductCreate, User

app = FastAPI(title="Swolez API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Swolez backend running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response

# ---------- Products Endpoints ----------

@app.get("/api/products", response_model=List[Product])
def list_products(line: Optional[str] = None, category: Optional[str] = None, featured: Optional[bool] = None):
    """List products with optional filters by line (gymwear/streetwear), category, and featured."""
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    query = {}
    if line:
        query["line"] = line
    if category:
        query["category"] = category
    if featured is not None:
        query["featured"] = featured

    docs = get_documents("product", query)

    # Convert ObjectId to str and ensure defaults
    results = []
    for d in docs:
        d.pop("_id", None)
        # Casting to Product will validate/normalize
        results.append(Product(**d))
    return results

@app.post("/api/products", status_code=201)
def create_product(payload: ProductCreate):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    prod_id = create_document("product", payload)
    return {"id": prod_id}

# ---------- Simple Seed Endpoint (optional helper) ----------

class SeedRequest(BaseModel):
    count: int = 6

@app.post("/api/seed")
def seed_products(req: SeedRequest):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    sample = [
        {
            "title": "Swolez Power Tee",
            "description": "Breathable performance tee with four-way stretch",
            "price": 28.0,
            "category": "tops",
            "line": "gymwear",
            "images": [
                "https://images.unsplash.com/photo-1592878849127-30a153c9fd1f?auto=format&fit=crop&w=1200&q=60"
            ],
            "colors": ["black", "white", "charcoal"],
            "sizes": ["S", "M", "L", "XL"],
            "in_stock": True,
            "featured": True,
            "rating": 4.6,
            "tags": ["tee", "gym", "stretch"]
        },
        {
            "title": "Swolez Street Hoodie",
            "description": "Heavyweight fleece with minimalist embroidery",
            "price": 64.0,
            "category": "hoodies",
            "line": "streetwear",
            "images": [
                "https://images.unsplash.com/photo-1548883354-7622d03aca9b?auto=format&fit=crop&w=1200&q=60"
            ],
            "colors": ["ash", "black", "forest"],
            "sizes": ["M", "L", "XL", "XXL"],
            "in_stock": True,
            "featured": True,
            "rating": 4.8,
            "tags": ["hoodie", "street", "fleece"]
        },
        {
            "title": "Swolez Flex Joggers",
            "description": "Tapered athletic fit with zip pockets",
            "price": 49.0,
            "category": "bottoms",
            "line": "gymwear",
            "images": [
                "https://images.unsplash.com/photo-1559631688-59c1ff16398d?auto=format&fit=crop&w=1200&q=60"
            ],
            "colors": ["black", "navy"],
            "sizes": ["S", "M", "L", "XL"],
            "in_stock": True,
            "featured": False,
            "rating": 4.5,
            "tags": ["joggers", "zip", "athletic"]
        },
        {
            "title": "Swolez Cargo Pants",
            "description": "Relaxed cargo with reinforced knees",
            "price": 59.0,
            "category": "bottoms",
            "line": "streetwear",
            "images": [
                "https://images.unsplash.com/photo-1539533018447-62fc810b90d9?auto=format&fit=crop&w=1200&q=60"
            ],
            "colors": ["khaki", "black"],
            "sizes": ["S", "M", "L", "XL", "XXL"],
            "in_stock": True,
            "featured": False,
            "rating": 4.4,
            "tags": ["cargo", "street"]
        },
        {
            "title": "Swolez Lift Beanie",
            "description": "Rib-knit beanie with woven label",
            "price": 18.0,
            "category": "accessories",
            "line": "streetwear",
            "images": [
                "https://images.unsplash.com/photo-1516571137133-1be29e37143a?auto=format&fit=crop&w=1200&q=60"
            ],
            "colors": ["black", "oxblood"],
            "sizes": [],
            "in_stock": True,
            "featured": False,
            "rating": 4.2,
            "tags": ["beanie", "winter"]
        },
        {
            "title": "Swolez Mesh Tank",
            "description": "Ultra-light mesh for max airflow",
            "price": 24.0,
            "category": "tops",
            "line": "gymwear",
            "images": [
                "https://images.unsplash.com/photo-1540573133985-87b6da6d54a9?auto=format&fit=crop&w=1200&q=60"
            ],
            "colors": ["white", "black"],
            "sizes": ["S", "M", "L"],
            "in_stock": True,
            "featured": False,
            "rating": 4.3,
            "tags": ["tank", "mesh", "breathable"]
        }
    ]

    created = 0
    for item in sample[: req.count]:
        create_document("product", item)
        created += 1
    return {"created": created}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
