from fastapi import FastAPI
from auth.routes import router as auth_router
from docs.routes import router as doc_router
from chat.routes import router as chat_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(doc_router)
app.include_router(chat_router)

@app.get("/health")
def health_check():
    return {
        "message" : "OK"
    }

