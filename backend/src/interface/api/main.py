from fastapi import FastAPI
from interface.api.routes import health, ingest, search, answer

app = FastAPI(title="RAG FAQ Backend")

# ルーター登録
app.include_router(health.router, tags=["health"])
app.include_router(ingest.router, tags=["ingest"])  
app.include_router(search.router, tags=["search"])
app.include_router(answer.router, tags=["answer"]) 

@app.get("/")
async def root():
    return {"message": "RAG FAQ Backend API", "status": "running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)