# LMS Backend — FastAPI Authentication API

A beginner-friendly FastAPI backend with **cookie-based JWT authentication** using SQLite3, SQLAlchemy, and Pydantic.

The backend runs at `http://localhost:8000` and is designed to work with a Next.js frontend at `http://localhost:3000`.

---

## Features

- User signup, login, logout
- JWT stored in **HttpOnly cookies** (not in response body or localStorage)
- Protected `/auth/me` route
- Password hashing with bcrypt (passlib)
- SQLite3 database with SQLAlchemy ORM
- CORS configured for credentials (cookies)

---

## Quick Start

### 1. Create a virtual environment

```bash
cd lms-be
python3 -m venv venv
source venv/bin/activate   # macOS / Linux
# venv\Scripts\activate    # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `.env` and update `JWT_SECRET_KEY` for production:

```env
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./lms.db
FRONTEND_URL=http://localhost:3000
```

### 4. Run the server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Project Structure

```
lms-be/
├── app/
│   ├── main.py              # FastAPI app + CORS
│   ├── database.py          # SQLAlchemy engine & session
│   ├── models/user.py       # User database model
│   ├── schemas/user.py      # Pydantic request/response schemas
│   ├── routes/auth.py       # Auth API routes
│   ├── core/
│   │   ├── config.py        # Settings from .env
│   │   └── security.py      # JWT + password hashing
│   └── dependencies/auth.py # get_current_user dependency
├── requirements.txt
├── .env
└── README.md
```

---

## API Endpoints

| Method | Endpoint       | Auth Required | Description              |
|--------|----------------|---------------|--------------------------|
| POST   | `/auth/signup` | No            | Register a new user      |
| POST   | `/auth/login`  | No            | Login and set cookie     |
| POST   | `/auth/logout` | No            | Clear auth cookie        |
| GET    | `/auth/me`     | Yes (cookie)  | Get current user         |

### POST `/auth/signup`

**Request body:**

```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response (201):**

```json
{
  "message": "Account created successfully",
  "user": {
    "id": 1,
    "full_name": "John Doe",
    "email": "john@example.com",
    "created_at": "2026-07-01T12:00:00Z"
  }
}
```

### POST `/auth/login`

**Request body:**

```json
{
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response (200):**

```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "full_name": "John Doe",
    "email": "john@example.com",
    "created_at": "2026-07-01T12:00:00Z"
  }
}
```

> **Important:** The JWT access token is **not** returned in the JSON body. It is set automatically in an HttpOnly cookie named `access_token`.

### POST `/auth/logout`

**Response (200):**

```json
{
  "message": "Logged out successfully"
}
```

Clears the `access_token` cookie.

### GET `/auth/me`

Requires the `access_token` HttpOnly cookie.

**Response (200):**

```json
{
  "id": 1,
  "full_name": "John Doe",
  "email": "john@example.com",
  "created_at": "2026-07-01T12:00:00Z"
}
```

**Error responses:**

| Status | Detail                              |
|--------|-------------------------------------|
| 400    | Email is already registered         |
| 401    | Invalid email or password           |
| 401    | Authentication token is missing     |
| 401    | Invalid or expired token            |

---

## HttpOnly Cookie Authentication

### How it works

1. User logs in with email and password.
2. Backend verifies credentials and generates a JWT.
3. Backend sets the JWT in a cookie with `httponly=True`.
4. The browser stores the cookie and sends it automatically on every request to the backend.
5. Frontend never sees or handles the token directly.

### Cookie settings (development)

```python
httponly=True    # JavaScript cannot read the cookie (XSS protection)
secure=False     # Set True in production (requires HTTPS)
samesite="lax"   # CSRF protection while allowing normal navigation
max_age=1800     # Matches JWT expiry (30 minutes)
```

### Production

When deploying with HTTPS, update `app/routes/auth.py`:

```python
secure=True  # Required for HTTPS production environments
```

Also use a strong, unique `JWT_SECRET_KEY` in your production `.env`.

---

## Why NOT localStorage?

| localStorage                         | HttpOnly Cookie                    |
|--------------------------------------|------------------------------------|
| Accessible by JavaScript             | Hidden from JavaScript             |
| Vulnerable to XSS attacks            | Protected against XSS token theft  |
| Manual token management in frontend  | Browser handles cookie automatically |
| Often stored in Redux/state too      | Token never touches frontend code  |

**Professional apps** store tokens in HttpOnly cookies so even if an XSS vulnerability exists, attackers cannot steal the JWT from `localStorage` or `sessionStorage`.

---

## Frontend Integration (Next.js + Axios + Redux)

### Axios setup (`src/lib/axiosInstance.js`)

```javascript
import axios from "axios";

const axiosInstance = axios.create({
  baseURL: "http://localhost:8000",
  headers: { "Content-Type": "application/json" },
  withCredentials: true, // Sends cookies automatically — do NOT use localStorage
});

export default axiosInstance;
```

**Rules:**

- Set `withCredentials: true` so cookies are sent with every request.
- Do **not** add an `Authorization` header manually.
- Do **not** store the token in localStorage, sessionStorage, or Redux.

### Example API calls

```javascript
// Signup
await axiosInstance.post("/auth/signup", { full_name, email, password });

// Login — backend sets HttpOnly cookie automatically
const { data } = await axiosInstance.post("/auth/login", { email, password });
// Store data.user in Redux only

// Get current user — cookie sent automatically
const { data: user } = await axiosInstance.get("/auth/me");

// Logout — backend clears cookie
await axiosInstance.post("/auth/logout");
// Clear Redux auth state
```

### Redux Toolkit auth state

Store only:

- `user` — user object from API
- `isAuthenticated` — boolean
- `loading` — boolean
- `error` — error message string

**Never store the JWT token in Redux.**

See `lms-next/src/features/auth/` for a complete working example with `authSlice.js` and `authThunks.js`.

---

## Error Handling

The API returns consistent HTTP status codes:

- **400** — Duplicate email on signup
- **401** — Wrong credentials, missing cookie, invalid or expired JWT
- **422** — Validation errors (invalid email format, short password, etc.)

Passwords are never returned in any response.

---

## License

MIT
