import httpx
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()

SHIPHERO_URL = "http://localhost:8001"
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

async def get_shiphero_inventory(sku: str) -> dict | None:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SHIPHERO_URL}/inventory/{sku}")
        if response.status_code != 200:
            return None
        data = response.json()
        node = data["data"]["warehouse_products"]["data"]["edges"][0]["node"]
        return {
            "on_hand": node["on_hand"],
            "reserve_inventory": node["reserve_inventory"]
        }

async def send_slack_alert(discrepancies: list):
    """Slack으로 불일치 알림 발송"""
    if not SLACK_WEBHOOK_URL:
        print("Slack Webhook URL 없음")
        return

    message = "재고 불일치 감지!\n\n"
    for d in discrepancies:
        message += (
            f"• SKU: {d['sku']}\n"
            f"  WMS: {d['wms_qty']}개 | "
            f"ShipHero: {d['shiphero_qty']}개 | "
            f"차이: {d['diff']}개\n"
            f"  감지 시각: {d['detected_at']}\n\n"
        )

    async with httpx.AsyncClient() as client:
        await client.post(
            SLACK_WEBHOOK_URL,
            json={"text": message}
        )
    print("===Slack 알림 발송 완료===")

async def detect_discrepancies(db) -> list:
    """자체 DB vs ShipHero 재고 불일치 감지"""
    discrepancies = []

    async with db.acquire() as conn:
        rows = await conn.fetch("""
            SELECT
                p.sku,
                il.quantity_on_hand AS wms_qty
            FROM inventory_levels il
            JOIN products p ON p.id = il.product_id
            JOIN channels c ON c.id = il.channel_id
            WHERE c.name = 'warehouse'
        """)

        for row in rows:
            sku = row['sku']
            wms_qty = row['wms_qty']

            shiphero = await get_shiphero_inventory(sku)
            if not shiphero:
                continue

            shiphero_qty = shiphero['on_hand']
            diff = wms_qty - shiphero_qty

            if diff != 0:
                discrepancy = {
                    "sku": sku,
                    "wms_qty": wms_qty,
                    "shiphero_qty": shiphero_qty,
                    "diff": diff,
                    "detected_at": datetime.now().isoformat()
                }
                discrepancies.append(discrepancy)
                print(f"===불일치 감지=== SKU: {sku} | WMS: {wms_qty} | ShipHero: {shiphero_qty} | 차이: {diff}")

    if discrepancies:
        await send_slack_alert(discrepancies)

    return discrepancies