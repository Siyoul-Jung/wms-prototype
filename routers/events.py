from fastapi import APIRouter, Depends
import json

router = APIRouter()

async def get_redis(request):
    return request.app.state.redis

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
        # 실제로는 여기서 Shopify/Amazon API 호출
        # 지금은 처리됐다고 출력만 함
        print(f"처리중: {event}")
        processed.append(event)
    return {"processed": processed, "count": len(processed)}