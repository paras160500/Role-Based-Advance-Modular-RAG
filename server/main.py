from fastapi import FastAPI
from auth.routes import router as auth_router

app = FastAPI()
app.include_router(auth_router)


@app.get("/health")
def health_check():
    return {
        "message" : "OK"
    }

