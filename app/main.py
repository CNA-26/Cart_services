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


@app.get("/status")
def get_status():
    return {
        "status": "alive",
        "service": "cart-service",
        "version": "0.1"
    }

