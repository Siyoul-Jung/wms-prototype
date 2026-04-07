# WMS Prototype

ShipHero 기반 멀티채널 이커머스 환경에서 발생하는 재고 불일치 
문제를 직접 분석하고 해결해보기 위해 설계한 자체 WMS 백엔드 
프로토타입입니다.

## 개요
멀티채널 재고 관리, 입출고 처리, ShipHero 재고 불일치 자동 
감지까지 지원하는 FastAPI 기반 백엔드 서버입니다. PostgreSQL을 
메인 DB로 사용하고, Redis를 이벤트 큐로 활용하여 비동기 이벤트 
처리를 지원합니다.

## 해결한 문제
- **SKU 매핑 수동 작업** → `sku_mappings` 테이블로 자동 변환
- **중복 주문 처리 버그** → Idempotency Key로 차단 (채널명 + 
  주문번호 조합, 동일 요청이 여러 번 들어와도 한 번만 처리)
- **채널 간 재고 불일치** → 이벤트 드리븐 큐로 자동 싱크
- **동시 주문 재고 이중 차감** → FOR UPDATE 락으로 방지
- **불일치 수동 감지** → ShipHero Mock API 연동으로 자동 감지 
  및 Slack 알림 발송

## 주요 기능
- 멀티채널 SKU 매핑 자동 변환 (Shopify/Amazon/Walmart)
- 입고/출고 API 및 재고 트랜잭션 처리
- PostgreSQL 트랜잭션 + FOR UPDATE 락으로 동시성 제어
- Idempotency Key 기반 중복 요청 차단
- Redis 이벤트 큐로 재고 변동 비동기 전파
- Shopify 웹훅 수신 및 자동 재고 처리
- ShipHero Mock API 연동으로 재고 불일치 자동 감지
- Slack Webhook으로 불일치 발견 시 실시간 알림

## 기술 스택
- **언어**: Python 3.11
- **프레임워크**: FastAPI
- **데이터베이스**: PostgreSQL
- **메시징/캐시**: Redis
- **외부 연동**: Shopify Webhook, ShipHero API (Mock), Slack Webhook

## 프로젝트 구조
- `main.py` : 서버 시작 및 라우터 등록
- `mock_shiphero.py` : ShipHero API Mock 서버 (포트 8001)
- `schema.sql` : PostgreSQL 테이블 구조 (DDL)
- `routers/` : API 엔드포인트 분리
  - `inventory.py` : 재고 조회, 입고, 출고 API
  - `webhook.py` : Shopify 웹훅 수신
  - `events.py` : 이벤트 조회 및 처리
  - `reconciliation.py` : 재고 불일치 감지 API
- `models/schemas.py` : Pydantic 요청/응답 모델
- `services/inventory.py` : 입출고 비즈니스 로직
- `services/reconciliation.py` : 불일치 감지 및 Slack 알림
- `db/connection.py` : DB / Redis 연결 관리

## 실행 방법
1. PostgreSQL에서 `schema.sql`을 실행합니다.
2. `.env` 파일에 DB 접속 정보와 Slack Webhook URL을 설정합니다.
3. Redis 실행:
```bash
docker run -d --name redis-wms -p 6379:6379 redis
```
4. Mock ShipHero 서버 실행 (새 터미널):
```bash
python mock_shiphero.py
```
5. WMS 서버 실행:
```bash
python -m uvicorn main:app --reload
```
6. API 문서 확인:
```text
http://127.0.0.1:8000/docs
```

## 예시 엔드포인트
- `GET /` : 헬스 체크
- `GET /inventory/{sku}` : SKU별 재고 조회
- `POST /inventory/inbound` : 입고 처리
- `POST /inventory/outbound` : 출고 처리
- `POST /webhook/shopify/order` : Shopify 주문 웹훅 수신
- `GET /events` : 이벤트 큐 조회
- `POST /events/process` : 이벤트 처리
- `POST /reconciliation/run` : 재고 불일치 감지 실행
- `GET /reconciliation/shiphero/{sku}` : ShipHero 재고 조회

## 참고
- 로컬에서 Redis와 PostgreSQL이 모두 실행되어 있어야 합니다.
- 실제 운영 환경에서는 DB 연결 정보를 환경 변수로 관리하는 것이 권장됩니다.