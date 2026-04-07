# WMS Prototype

ShipHero의 한계를 보완하는 자체 WMS 백엔드 프로토타입

## 기술 스택
- Python 3.11
- FastAPI
- PostgreSQL
- Redis (이벤트 큐)

## 해결한 문제
- 멀티채널 SKU 매핑 자동화 (Shopify/Amazon/Walmart)
- 트랜잭션으로 재고 데이터 일관성 보장
- Idempotency Key로 중복 주문 처리 방지
- 이벤트 드리븐 아키텍처로 채널 간 재고 자동 싱크

## 실행 방법
1. PostgreSQL에서 schema.sql 실행
2. main.py DB 비밀번호 설정
3. uvicorn main:app --reload
4. http://127.0.0.1:8000/docs 접속