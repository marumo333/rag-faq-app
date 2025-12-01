from fastapi import FastAPI  
from interface.api.routes import router

app = FastAPI(title = "RAG FAQ Backend")

app.include_router(health_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)