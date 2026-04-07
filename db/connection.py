import asyncpg
import redis as redis_client
import os
from fastapi import Request
from dotenv import load_dotenv
load_dotenv()

DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "port":     int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME", "wms_dev"),
    "user":     os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
}

async def create_db_pool():
    return await asyncpg.create_pool(**DB_CONFIG)

def create_redis_client():
    return redis_client.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        decode_responses=True
    )

async def startup_event(app):
    app.state.db = await create_db_pool()
    app.state.redis = create_redis_client()
    print("DB 연결 완료!")
    print("Redis 연결 완료!")

async def shutdown_event(app):
    await app.state.db.close()


def get_db(request: Request):
    return request.app.state.db

def get_redis(request: Request):
    return request.app.state.redis