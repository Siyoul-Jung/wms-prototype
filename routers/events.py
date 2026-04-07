from fastapi import APIRouter, Depends
import json
from db.connection import get_redis

router = APIRouter()

@router.get("/events")
async def get_events(redis=Depends(get_redis)):
    """큐에 쌓인 이벤트 확인용"""
    events = redis.lrange("inventory_events", 0, -1)
    return {"events": [json.loads(e) for e in events]}

@router.post("/events/process")
async def process_events(redis=Depends(get_redis)):
    """큐에 쌓인 이벤트 처리"""
    processed = []
    while True:
        event_data = redis.lpop("inventory_events")
        if not event_data:
            break
        event = json.loads(event_data)

        # TODO: 실제 운영 환경에서는 아래 작업 수행
        # - Shopify API로 재고 업데이트 전송
        # - Amazon API로 재고 업데이트 전송
        # - 실패 시 dead letter queue로 이동하여 재시도
        print(f"처리중: {event}")

        processed.append(event)
    return {"processed": processed, "count": len(processed)}