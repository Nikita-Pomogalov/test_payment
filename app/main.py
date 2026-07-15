from fastapi import FastAPI

app = FastAPI(title="Payment System API", version="1.0.0")


@app.get("/")
async def root():
    return {"message": "Payment System API is running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}