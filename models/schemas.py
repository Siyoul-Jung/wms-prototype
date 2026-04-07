from pydantic import BaseModel

class OutboundRequest(BaseModel):
    channel_sku: str
    channel:     str
    quantity:    int
    order_id:    str  # idempotency_key로 사용

class ShopifyWebhookRequest(BaseModel):
    order_id: str
    line_items: list  # 주문 상품 목록