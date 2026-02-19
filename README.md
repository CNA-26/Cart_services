# Cart Service 🛒

Detta är en Microservice som hanterar varukorgen för butiken
Just nu körs den med mock data för att möjliggöra frontend-utveckling utan databas.

API URL: https://cart-services-git-cartservices.2.rahtiapp.fi

**Endpoints:**

- **GET** `/cart/{user_id}` - Hämta cart
- **POST** `/cart/{user_id}/add-item` - Lägg till item
- **DELETE** `/cart/{user_id}/item/{product_id}` - Ta bort item

---

## Kom igång

Skapa och aktivera virtuell miljö:

```bash
python3 -m venv .venv
source .venv/bin/activate  # (Mac/Linux)
.venv\Scripts\activate  # (Windows)

```

installera requirements:

```bash
pip install -r requirements.txt
```

starta servern lokalt:

```bash
uvicorn main:app --reload
```

---

### Api dokumentation

FastAPI kommer mer automatisk swagger dokumentation, man kan testa endpoints när servern snurrar:
http://127.0.0.1:8000/docs

#### Exempel

om man kör en GET på /cart/user_123 får man detta:

```json
{
  "user_123": {
    "user_id": "user_123",
    "items": [
      {
        "product_id": 101,
        "name": "Monstera",
        "price": 30.0,
        "quantity": 1,
        "image_url": "https://example.com/monstera.jpg"
      }
    ],
    "total_price": 30.0
  }
}
```

**OBS** datan är hårdkodad placeholder, men exempelvis kunde man kunna använda sig av detta format
