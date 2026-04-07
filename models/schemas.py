from pydantic import BaseModel
from typing import List

class OutboundRequest(BaseModel):
    channel_sku: str
    channel:     str
    quantity:    int
    order_id:    str  # idempotency_key로 사용

class LineItem(BaseModel):
    sku:      str
    quantity: int

class ShopifyWebhookRequest(BaseModel):
    order_id:   str
    line_items: List[LineItem]  

class InboundRequest(BaseModel):
    channel_sku: str
    channel:     str
    quantity:    int
    order_id:    str