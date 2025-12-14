from fastapi import FastAPI
from interface.api.routes import health  

app = FastAPI(title="RAG FAQ Backend")

# healthルーターを登録
app.include_router(health.router, tags=["health"])

@app.get("/")
async def root():
    return {"message": "RAG FAQ Backend API", "status": "running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)