from fastapi import APIRouter, Depends
from services.inventory import process_outbound
from models.schemas import OutboundRequest

router = APIRouter()

async def get_db(request):
    return request.app.state.db

async def get_redis(request):
    return request.app.state.redis

@router.get("/inventory/{sku}")
async def get_inventory(sku: str, db=Depends(get_db)):
    async with db.acquire() as conn:
        rows = await conn.fetch("""
            SELECT
                c.name AS channel,
                il.quantity_on_hand,
                il.quantity_on_hand - il.quantity_reserved AS available
            FROM inventory_levels il
            JOIN products p ON p.id = il.product_id
            JOIN channels c ON c.id = il.channel_id
            WHERE p.sku = $1
        """, sku)
    return {"sku": sku, "inventory": [dict(r) for r in rows]}

@router.post("/inventory/outbound")
async def outbound(req: OutboundRequest, db=Depends(get_db), redis=Depends(get_redis)):
    return await process_outbound(req, db, redis)