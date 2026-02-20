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
uvicorn app.main:app --reload
```

---

## Placeholder auth (API-key)

Alla endpoints under `/cart/*` kräver en API-nyckel.

- **Header**: `Authorization: ApiKey <key>`
- **Miljövariabel**: `PLACEHOLDER_API_KEY`

```

---

## JWT (spec)

När placeholder auth ersätts av JWT ska cart-service använda:

- **Header**: `Authorization: Bearer <jwt>`
- **Alg**: `HS256` (via `JWT_SECRET`) eller senare `RS256` via JWKS (om auth-service tillhandahåller det)
- **Required claims**: `sub`, `exp` (och vid behov `iss`, `aud`)

Regel:

- För kundanrop ska `user_id` i path matcha token-claim `sub` (annars `403`).

### Api dokumentation

FastAPI kommer mer automatisk swagger dokumentation, man kan testa endpoints när servern snurrar:
http://127.0.0.1:8000/docs
