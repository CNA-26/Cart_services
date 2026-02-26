from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from jose import JWTError, jwt
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


def get_current_user(authorization: str | None = Header(default=None)) -> str:
    jwt_secret = os.getenv("JWT_SECRET")
    if not jwt_secret:
        raise HTTPException(status_code=500, detail="JWT_SECRET is not configured")

    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, 
            detail="Invalid Authorization scheme. Expected: Bearer <token>"
        )

    token = authorization[7:].strip()  # Remove "Bearer " prefix
        
    try:
        # Decodes JWT using HS256 algorithm with JWT_SECRET
        payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
        
        # Extract user_id from 'sub' claim
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token: missing 'sub' claim")
        
        return user_id
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid or expired token: {str(e)}")

@app.get("/")
def read_root():
    return {"status": "Cart Service is running", "docs": "/docs"}


@app.get("/cart/{user_id}", response_model=Cart)
def get_cart_endpoint(user_id: str, current_user: str = Depends(get_current_user)):
    # Verify user can only access their own cart
    if user_id != current_user:
        raise HTTPException(
            status_code=403, 
            detail="Access denied: user_id in path must match token subject"
        )
    
    cart = database.get_cart(user_id)
    if cart is None:
        raise HTTPException(status_code=500, detail="Database connection error")
    return cart


@app.post("/cart/{user_id}/add-item")
def add_item_to_cart_endpoint(
    user_id: str, 
    item: AddItemRequest,
    current_user: str = Depends(get_current_user)
):

    if user_id != current_user:
        raise HTTPException(
            status_code=403, 
            detail="Access denied: user_id in path must match token subject"
        )
    
    cart = database.add_item_to_cart(user_id, item.dict())
    if cart is None:
        raise HTTPException(status_code=500, detail="Database connection error")
    return cart


@app.delete("/cart/{user_id}/item/{product_id}")
def remove_item_from_cart_endpoint(
    user_id: str, 
    product_id: int,
    current_user: str = Depends(get_current_user)
):
    # User verification
    if user_id != current_user:
        raise HTTPException(
            status_code=403, 
            detail="Access denied: user_id in path must match token subject"
        )
    
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

