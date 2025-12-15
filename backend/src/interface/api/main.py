from fastapi import FastAPI
from interface.api.routes import health, ingest

app = FastAPI(title="RAG FAQ Backend")

# ルーター登録
app.include_router(health.router, tags=["health"])
app.include_router(ingest.router, tags=["ingest"])  

@app.get("/")
async def root():
    return {"message": "RAG FAQ Backend API", "status": "running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)