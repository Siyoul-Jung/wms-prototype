from fastapi import APIRouter, Depends
from services.reconciliation import detect_discrepancies
from db.connection import get_db

router = APIRouter()

@router.post("/reconciliation/run")
async def run_reconciliation(db=Depends(get_db)):
    """재고 불일치 감지 실행"""
    discrepancies = await detect_discrepancies(db)

    if not discrepancies:
        return {
            "status": "ok",
            "message": "불일치 없음. 모든 재고 정상",
            "count": 0
        }

    return {
        "status": "discrepancy_found",
        "message": f"{len(discrepancies)}개 SKU에서 불일치 감지",
        "count": len(discrepancies),
        "discrepancies": discrepancies
    }

@router.get("/reconciliation/shiphero/{sku}")
async def get_shiphero_stock(sku: str):
    """ShipHero 재고 직접 조회 (비교용)"""
    from services.reconciliation import get_shiphero_inventory
    result = await get_shiphero_inventory(sku)
    if not result:
        return {"error": "ShipHero에서 SKU를 찾을 수 없음"}
    return {"sku": sku, "shiphero": result}