from fastapi import APIRouter, Depends
from services.inventory import process_outbound
from models.schemas import OutboundRequest, ShopifyWebhookRequest

router = APIRouter()

async def get_db(request):
    return request.app.state.db

async def get_redis(request):
    return request.app.state.redis

@router.post("/webhook/shopify/order")
async def shopify_webhook(req: ShopifyWebhookRequest, db=Depends(get_db), redis=Depends(get_redis)):
    """Shopify 주문 웹훅 수신"""
    results = []

    for item in req.line_items:
        # 각 주문 상품을 outbound API로 처리
        outbound_req = OutboundRequest(
            channel_sku=item['sku'],
            channel='shopify',
            quantity=item['quantity'],
            order_id=f"{req.order_id}-{item['sku']}"
        )
        result = await process_outbound(outbound_req, db, redis)
        results.append(result)

    return {
        "status": "ok",
        "order_id": req.order_id,
        "results": results
    }