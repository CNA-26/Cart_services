from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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

# Mock data, placeholder for database
mock_db = {
    "user_123": {
        "user_id": "user_123",
        "items": [
            {
                "product_id": 101, 
                "name": "Monstera", 
                "price": 30.00, 
                "quantity": 1,
                "image_url": "https://example.com/monstera.jpg" 
            }
        ],
        "total_price": 30.00
    }
}

@app.get("/")
def read_root():
    return {"status": "Cart Service is running", "docs": "/docs"}


@app.get("/cart/{user_id}", response_model=Cart)
def get_cart(user_id: str):
    if user_id in mock_db:
        return mock_db[user_id]
    
    return {
        "user_id": user_id,
        "items": [],
        "total_price": 0.0
    }


@app.post("/cart/{user_id}/add-item")
def add_item_to_cart(user_id: str, item: AddItemRequest):
    
    # Skapa tom cart om den inte finns
    if user_id not in mock_db:
        mock_db[user_id] = {"user_id": user_id, "items": [], "total_price": 0.0}
    
    cart = mock_db[user_id]
    
    # Hitta item eller lägg till nytt
    for cart_item in cart["items"]:
        if cart_item["product_id"] == item.product_id:
            cart_item["quantity"] += item.quantity
            break
    else:
        
        cart["items"].append(item.dict())
    
    # Räkna om total
    cart["total_price"] = sum(i["price"] * i["quantity"] for i in cart["items"])
    
    return cart


@app.delete("/cart/{user_id}/item/{product_id}")
def remove_item_from_cart(user_id: str, product_id: int):
    
    if user_id not in mock_db:
        return {"error": "Cart not found"}
    
    cart = mock_db[user_id]
    
    # Hitta och ta bort item
    for i, cart_item in enumerate(cart["items"]):
        if cart_item["product_id"] == product_id:
            removed_item = cart["items"].pop(i)
            break
    else:
        return {"error": "Item not found in cart"}
    
    # Räkna om total
    cart["total_price"] = sum(i["price"] * i["quantity"] for i in cart["items"])
    
    return {"message": "Item removed", "removed_item": removed_item, "cart": cart}


@app.get("/status")
def get_status():
    return {
        "status": "alive",
        "service": "cart-service",
        "version": "0.1"
    }

