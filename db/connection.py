import asyncpg
import redis as redis_client

DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "database": "wms_dev",
    "user":     "postgres",
    "password": "postgres"  # pgAdmin 접속할 때 쓰는 비밀번호
}

async def create_db_pool():
    return await asyncpg.create_pool(**DB_CONFIG)

def create_redis_client():
    return redis_client.Redis(host='localhost', port=6379, decode_responses=True)

async def startup_event(app):
    app.state.db = await create_db_pool()
    app.state.redis = create_redis_client()
    print("DB 연결 완료!")
    print("Redis 연결 완료!")

async def shutdown_event(app):
    await app.state.db.close()