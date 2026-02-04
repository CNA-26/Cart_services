from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return { "msg": "Hello!", "v": "0.1" }


@app.get("/items/{id}")
def read_item(item_id: int, q: str = None):
    return {"id": id, "q": q}


@app.get("/status")
def get_status():
    return {
        "status": "alive",
        "service": "cart-service",
        "version": "0.1"
    }

