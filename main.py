from dotenv import load_dotenv
from fastapi import FastAPI
# Routers
from routers import default

app = FastAPI()
@app.on_event("startup")
async def startup_event():
    # print("app ready")
    load_dotenv()
app.include_router(default.router, prefix="/api/v1")
