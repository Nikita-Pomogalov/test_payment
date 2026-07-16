from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api import auth, users, admin, webhook
from app.database import db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect()
    print("✅ Database connected")
    yield
    await db.disconnect()
    print("✅ Database disconnected")

app = FastAPI(
    title="Payment System API",
    version="1.0.0",
    description="Payment System with webhook support",
    lifespan=lifespan
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(webhook.router)

@app.get("/")
async def root():
    return {"message": "Payment System API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}