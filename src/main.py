from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.routers import auth, users, products, inventory, transactions

app = FastAPI(
    title="Boarder Management API",
    description="A REST API for managing products, stock levels, and transactions.",
    version="1.0.0",
)

# ── CORS ──────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # restrict to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(inventory.router)
app.include_router(transactions.router)


# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Boarder Management API is running"}


# ── Static UI ─────────────────────────────────────────────────────────────────

UI_DIR = Path(__file__).parent.parent / "ui"
app.mount("/ui", StaticFiles(directory=UI_DIR, html=True), name="ui")
