import redis
from backend.core.config import settings

r = redis.from_url(settings.REDIS_URL, decode_responses=True)

def incr_and_check(ip: str, key: str, limit: int, window: int = 60) -> bool:
    bucket = f"rate:{key}:{ip}"
    val = r.incr(bucket)
    if val == 1:
        r.expire(bucket, window)
    return val <= limit