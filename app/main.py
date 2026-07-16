from fastapi import FastAPI
from app.api import auth, users
from app.database import db


app = FastAPI(
    title="Payment System API",
    version="1.0.0",
    description="Payment System with webhook support"
)

# Подключаем роутеры
app.include_router(auth.router)
app.include_router(users.router)

@app.get("/")
async def root():
    return {"message": "Payment System API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.on_event("startup")
async def startup():
    """Подключение к БД при старте"""
    await db.connect()
    print("✅ Database connected")

@app.on_event("shutdown")
async def shutdown():
    """Отключение от БД при остановке"""
    await db.disconnect()
    print("✅ Database disconnected")