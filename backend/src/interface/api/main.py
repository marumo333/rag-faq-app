from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
from interface.api.routes import health, ingest, search, answer, documents

app = FastAPI(title="RAG FAQ Backend")

# CORS settings
origins = [
    # ローカル開発用
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    # 本番フロントエンド（Vercel）
    "https://rag-faq-app.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーター登録
app.include_router(health.router, tags=["health"])
app.include_router(ingest.router, tags=["ingest"])  
app.include_router(search.router, tags=["search"])
app.include_router(answer.router, tags=["answer"]) 
app.include_router(documents.router, tags=["documents"])

@app.get("/")
async def root() -> Dict[str, str]:
    return {"message": "RAG FAQ Backend API", "status": "running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)