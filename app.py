from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import asyncpg
import os

app = FastAPI()

# Middleware per gestire le sessioni utente
app.add_middleware(SessionMiddleware, secret_key="supersecret")

# Static & template directories
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# PostgreSQL connection string
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://talfy_db_user:...")  # aggiorna qui

# Connessione DB
async def get_db():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        await conn.close()

# === ROTTA HOMEPAGE / CONTATORI ===
@app.get("/api/stats")
async def get_stats(db=Depends(get_db)):
    total_candidates = await db.fetchval("SELECT COUNT(*) FROM candidates")
    total_companies = await db.fetchval("SELECT COUNT(*) FROM companies")
    return {
        "candidates": total_candidates,
        "companies": total_companies
    }

# === REGISTRAZIONE ===
@app.post("/api/register")
async def register_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    user_type: str = Form(...)  # 'candidate' o 'company'
):
    if password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    db = await anext(get_db())
    table = "candidates" if user_type == "candidate" else "companies"

    existing = await db.fetchval(f"SELECT COUNT(*) FROM {table} WHERE email=$1", email)
    if existing > 0:
        raise HTTPException(status_code=400, detail="User already exists")

    await db.execute(
        f"INSERT INTO {table} (email, password) VALUES ($1, $2)",
        email, password  # NB: Da cifrare con hashing!
    )

    request.session["user"] = {"email": email, "type": user_type}

    if user_type == "candidate":
        return RedirectResponse("/complete-profile-candidate.html", status_code=302)
    else:
        return RedirectResponse("/complete-profile-company.html", status_code=302)

# === LOGIN ===
@app.post("/api/login")
async def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    db = await anext(get_db())

    for table in ["candidates", "companies"]:
        user = await db.fetchrow(
            f"SELECT * FROM {table} WHERE email=$1 AND password=$2",
            email, password  # NB: Da cifrare con hashing!
        )
        if user:
            request.session["user"] = {"email": email, "type": table[:-1]}
            return RedirectResponse("/index.html", status_code=302)

    raise HTTPException(status_code=401, detail="Invalid credentials")

# === CHECK LOGIN (per pagine plan) ===
@app.get("/check-login")
async def check_login(request: Request):
    user = request.session.get("user")
    if user:
        return {"logged_in": True, "user_type": user["type"]}
    return {"logged_in": False}

# === LOGOUT ===
@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/index.html", status_code=302)
