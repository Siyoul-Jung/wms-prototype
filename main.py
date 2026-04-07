from fastapi import FastAPI
from db.connection import startup_event, shutdown_event
from routers import inventory, webhook, events, reconciliation

app = FastAPI()

@app.on_event("startup")
async def startup():
    await startup_event(app)

@app.on_event("shutdown")
async def shutdown():
    await shutdown_event(app)

@app.get("/")
async def health_check():
    return {"status": "ok", "message": "WMS 서버 작동중"}

# 라우터 등록
app.include_router(inventory.router)
app.include_router(webhook.router)
app.include_router(events.router)
app.include_router(reconciliation.router)