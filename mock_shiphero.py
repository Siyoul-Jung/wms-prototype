from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Mock ShipHero API")

# 고의적 자체 DB와 불일치 재고 데이터 설정
MOCK_INVENTORY = {
    "ICC-COVER-001-BLK-M": {
        "on_hand": 75,        # 자체 DB는 82개인데 ShipHero는 75개일 경우 가정
        "reserve_inventory": 2
    }
}

@app.get("/inventory/{sku}")
def get_inventory(sku: str):
    """ShipHero warehouse_products API 구조 흉내"""
    inventory = MOCK_INVENTORY.get(sku)
    if not inventory:
        return {"error": f"SKU not found: {sku}"}
    return {
        "data": {
            "warehouse_products": {
                "data": {
                    "edges": [{
                        "node": {
                            "on_hand": inventory["on_hand"],
                            "reserve_inventory": inventory["reserve_inventory"],
                            "product": {"sku": sku}
                        }
                    }]
                }
            }
        }
    }

@app.put("/inventory/{sku}")
def update_inventory(sku: str, on_hand: int):
    """ShipHero inventory_replace mutation 흉내"""
    if sku not in MOCK_INVENTORY:
        return {"error": f"SKU not found: {sku}"}
    MOCK_INVENTORY[sku]["on_hand"] = on_hand
    return {"status": "ok", "sku": sku, "on_hand": on_hand}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)   