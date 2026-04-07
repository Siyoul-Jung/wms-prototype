# WMS Prototype

ShipHero의 한계를 보완하기 위해 만든 자체 WMS 백엔드 프로토타입입니다.

## 🌟 개요
이 프로젝트는 멀티채널 재고 관리와 주문 출고 처리를 위한 FastAPI 기반 서버입니다. PostgreSQL을 메인 DB로 사용하고, Redis를 이벤트 큐로 활용하여 비동기 이벤트 처리를 지원합니다.

## 🧱 주요 기능
- 멀티채널 SKU 매핑 자동 변환
- PostgreSQL 트랜잭션으로 재고 일관성 보장
- Idempotency Key 기반 중복 주문 방지
- Redis 이벤트 큐를 사용한 이벤트 드리븐 재고 동기화

## 🛠️ 기술 스택
- Python 3.11
- FastAPI
- PostgreSQL
- Redis

## 📁 프로젝트 구조
- `main.py` : 서버 시작 및 라우터 등록
- `routers/` : API 엔드포인트 분리
  - `inventory.py` : 재고 조회 및 출고 API
  - `webhook.py` : Shopify 웹훅 수신
  - `events.py` : 이벤트 조회 및 처리
- `models/schemas.py` : Pydantic 요청/응답 모델
- `services/inventory.py` : 비즈니스 로직 구현
- `db/connection.py` : DB / Redis 연결 관리

## 🚀 실행 방법
1. PostgreSQL에서 필요한 스키마를 생성합니다.
2. `db/connection.py` 또는 설정 파일에서 DB 접속 정보를 확인합니다.
3. 프로젝트 루트에서 아래 명령을 실행합니다:

```bash
python -m uvicorn main:app --reload
```

4. 브라우저에서 API 문서를 확인합니다:

```text
http://127.0.0.1:8000/docs
```

## 📌 예시 엔드포인트
- `GET /` : 헬스 체크
- `GET /inventory/{sku}` : SKU별 재고 조회
- `POST /inventory/outbound` : 출고 처리
- `POST /webhook/shopify/order` : Shopify 주문 웹훅 수신
- `GET /events` : 이벤트 큐 조회
- `POST /events/process` : 이벤트 처리

## 💡 참고
- 로컬에서 Redis와 PostgreSQL이 모두 실행되어 있어야 합니다.
- 실제 운영 환경에서는 DB 연결 정보와 비밀번호를 환경 변수로 관리하는 것이 안전합니다.