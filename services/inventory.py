import json
from models.schemas import OutboundRequest

async def process_outbound(req: OutboundRequest, db_pool, redis_client):
    async with db_pool.acquire() as conn:
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
            redis_client.rpush("inventory_events", json.dumps(event))

    return {
        "status":    "ok",
        "master_sku": product['sku'],
        "remaining":  updated['quantity_on_hand']
    }