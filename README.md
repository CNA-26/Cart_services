# Cart Service 🛒

Detta är en Microservice som hanterar varukorgen för butiken.
Tjänsten använder PostgreSQL-databas och JWT-autentisering.

**API URL:** https://cart-services-git-cartservices.2.rahtiapp.fi

## Endpoints:

- **GET** `/cart/{user_id}` - Hämta cart
- **POST** `/cart/{user_id}/add-item` - Lägg till item
- **DELETE** `/cart/{user_id}/item/{product_id}` - Ta bort item

---

## Autentisering

Alla endpoints under `/cart/*` kräver en giltig JWT token i Authorization headern

---

- **Header**: `Authorization: Bearer <jwt-token>`
- **Alg**: `HS256`
- **Required claims**: `sub` (user_id), `exp` (utgångstid)
- **Optional claims**: `aud`, `iss`, dessa valideras **ej**
- `email`, `role`, `iat`

---

### Api dokumentation

FastAPI kommer mer automatisk swagger dokumentation, man kan testa endpoints när servern snurrar:
https://cart-services-git-cartservices.2.rahtiapp.fi/docs
eller lokalt:
http://127.0.0.1:8000/docs

---

## Kom igång lokalt

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
