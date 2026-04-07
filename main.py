from fastapi import FastAPI
import asyncpg
import redis as redis_client

app = FastAPI()

DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "database": "wms_dev",
    "user":     "postgres",
    "password": "postgres"  # pgAdmin 접속할 때 쓰는 비밀번호
}

@app.on_event("startup")
async def startup():
    app.state.db = await asyncpg.create_pool(**DB_CONFIG)
    app.state.redis = redis_client.Redis(host='localhost', port=6379, decode_responses=True)
    print("DB 연결 완료!")
    print("Redis 연결 완료!")

@app.on_event("shutdown")
async def shutdown():
    await app.state.db.close()

@app.get("/")
async def health_check():
    return {"status": "ok", "message": "WMS 서버 작동중"}

@app.get("/inventory/{sku}")
async def get_inventory(sku: str):
    async with app.state.db.acquire() as conn:
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

from pydantic import BaseModel

class OutboundRequest(BaseModel):
    channel_sku: str
    channel:     str
    quantity:    int
    order_id:    str  # idempotency_key로 사용

@app.post("/inventory/outbound")
async def outbound(req: OutboundRequest):
    async with app.state.db.acquire() as conn:
        async with conn.transaction():  # 트랜잭션 시작

            # 1. 채널 SKU → 마스터 SKU 변환
            product = await conn.fetchrow("""
                SELECT p.id, p.sku
                FROM sku_mappings sm
                JOIN products p ON p.id = sm.product_id
                JOIN channels c ON c.id = sm.channel_id
                WHERE c.name = $1 AND sm.channel_sku = $2
                  AND sm.is_active = TRUE
            """, req.channel, req.channel_sku)

            if not product:
                return {"error": f"알 수 없는 SKU: {req.channel_sku}"}

            # 2. 중복 요청 확인 (idempotency)
            idempotency_key = f"{req.channel}-{req.order_id}-outbound"
            existing = await conn.fetchrow("""
                SELECT id FROM inventory_transactions
                WHERE idempotency_key = $1
            """, idempotency_key)

            if existing:
                return {"status": "already_processed", "order_id": req.order_id}

            # 3. 재고 차감 (칠판)
            channel = await conn.fetchrow(
                "SELECT id FROM channels WHERE name = $1", 'warehouse'
            )
            updated = await conn.fetchrow("""
                UPDATE inventory_levels
                SET quantity_on_hand = quantity_on_hand - $1,
                    updated_at = NOW()
                WHERE product_id = $2 AND channel_id = $3
                  AND quantity_on_hand >= $1
                RETURNING quantity_on_hand
            """, req.quantity, product['id'], channel['id'])

            if not updated:
                return {"error": "재고 부족"}

            # 4. 이력 기록 (영수증)
            await conn.execute("""
                INSERT INTO inventory_transactions
                    (product_id, channel_id, type, quantity_delta,
                     note, idempotency_key)
                VALUES ($1, $2, 'outbound', $3, $4, $5)
            """, product['id'], channel['id'],
                -req.quantity,
                f"{req.channel} 주문 #{req.order_id}",
                idempotency_key)
            
            # 5. 이벤트 큐에 던지기
            event = {
                "type": "inventory_updated",
                "master_sku": product['sku'],
                "channel": req.channel,
                "quantity_delta": -req.quantity,
                "remaining": updated['quantity_on_hand']
            }
            app.state.redis.rpush("inventory_events", json.dumps(event))

    return {
        "status":    "ok",
        "master_sku": product['sku'],
        "remaining":  updated['quantity_on_hand']
    }    

import json

@app.get("/events")
async def get_events():
    """큐에 쌓인 이벤트 확인용"""
    events = app.state.redis.lrange("inventory_events", 0, -1)
    return {"events": [json.loads(e) for e in events]}

@app.post("/events/process")
async def process_events():
    """큐에 쌓인 이벤트 처리"""
    processed = []
    while True:
        event_data = app.state.redis.lpop("inventory_events")
        if not event_data:
            break
        event = json.loads(event_data)
        # 실제로는 여기서 Shopify/Amazon API 호출
        # 지금은 처리됐다고 출력만 함
        print(f"처리중: {event}")
        processed.append(event)
    return {"processed": processed, "count": len(processed)}