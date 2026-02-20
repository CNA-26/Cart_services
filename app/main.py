from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from . import database

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CartItem(BaseModel):
    product_id: int
    name: str
    price: float
    quantity: int
    image_url: str

class Cart(BaseModel):
    user_id: str
    items: list[CartItem]
    total_price: float

class AddItemRequest(BaseModel):
    product_id: int
    name: str
    price: float
    quantity: int = 1
    image_url: str

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    database.init_database()

@app.get("/")
def read_root():
    return {"status": "Cart Service is running", "docs": "/docs"}


@app.get("/cart/{user_id}", response_model=Cart)
def get_cart_endpoint(user_id: str):
    cart = database.get_cart(user_id)
    if cart is None:
        raise HTTPException(status_code=500, detail="Database connection error")
    return cart


@app.post("/cart/{user_id}/add-item")
def add_item_to_cart_endpoint(user_id: str, item: AddItemRequest):
    cart = database.add_item_to_cart(user_id, item.dict())
    if cart is None:
        raise HTTPException(status_code=500, detail="Database connection error")
    return cart


@app.delete("/cart/{user_id}/item/{product_id}")
def remove_item_from_cart_endpoint(user_id: str, product_id: int):
    result = database.remove_item_from_cart(user_id, product_id)
    if result is None:
        raise HTTPException(status_code=500, detail="Database connection error")
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@app.get("/status")
def get_status():
    return {
        "status": "alive",
        "service": "cart-service",
        "version": "0.1"
    }

