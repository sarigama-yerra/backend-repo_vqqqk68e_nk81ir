"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Literal

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: Literal["tops", "bottoms", "hoodies", "accessories"] = Field(..., description="Product category")
    line: Literal["gymwear", "streetwear"] = Field(..., description="Brand line")
    images: List[HttpUrl] = Field(default_factory=list, description="Image URLs")
    colors: List[str] = Field(default_factory=list, description="Available colors")
    sizes: List[Literal["XS", "S", "M", "L", "XL", "XXL"]] = Field(default_factory=list, description="Available sizes")
    in_stock: bool = Field(True, description="Whether product is in stock")
    featured: bool = Field(False, description="Featured product for landing")
    rating: Optional[float] = Field(None, ge=0, le=5, description="Average rating")
    tags: List[str] = Field(default_factory=list, description="Searchable tags")

# Lightweight model for creates where URLs might not be strict
class ProductCreate(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: Literal["tops", "bottoms", "hoodies", "accessories"]
    line: Literal["gymwear", "streetwear"]
    images: List[str] = []
    colors: List[str] = []
    sizes: List[Literal["XS", "S", "M", "L", "XL", "XXL"]] = []
    in_stock: bool = True
    featured: bool = False
    rating: Optional[float] = None
    tags: List[str] = []

# The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
