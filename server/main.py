from fastapi import FastAPI
from auth.routes import router as auth_router
from docs.routes import router as doc_router
from chat.routes import router as chat_router
from pymongo import MongoClient
import certifi
import traceback,os

app = FastAPI()
app.include_router(auth_router)
app.include_router(doc_router)
app.include_router(chat_router)

@app.get("/health")
def health_check():
    return {
        "message" : "OK"
    }

@app.get("/mongo")
def mongo_test():
    try:
        client = MongoClient(
            os.getenv("MONGO_URI"),
            tls=True,
            tlsCAFile=certifi.where(),
        )

        client.admin.command("ping")
        return {"status": "connected successfully."}

    except Exception as e:
        return {
            "error": str(e),
            "type": str(type(e)),
            "trace": traceback.format_exc() 
        }
