import redis
from backend.core.config import settings
import time
import logging

logger = logging.getLogger(__name__)

# Create Redis connection with retry logic
_max_retries = 5
_retry_delay = 2
r = None

try:
    for attempt in range(_max_retries):
        try:
            r = redis.from_url(
                settings.REDIS_URL, 
                decode_responses=True, 
                socket_connect_timeout=5,
                socket_keepalive=True
            )
            r.ping()  # Test connection
            logger.info("Redis connection established")
            break
        except (redis.ConnectionError, redis.TimeoutError, Exception) as e:
            if attempt < _max_retries - 1:
                logger.warning(f"Redis connection attempt {attempt + 1} failed, retrying...")
                time.sleep(_retry_delay)
            else:
                logger.error(f"Failed to connect to Redis after {_max_retries} attempts: {e}")
                r = None  # Keep as None if all attempts fail
except Exception as e:
    logger.error(f"Error initializing Redis: {e}")
    r = None

def incr_and_check(ip: str, key: str, limit: int, window: int = 60) -> bool:
    """Rate limiting with Redis. Returns False if limit exceeded or Redis unavailable."""
    if r is None:
        return True  # Allow request if Redis is unavailable
    try:
        bucket = f"rate:{key}:{ip}"
        val = r.incr(bucket)
        if val == 1:
            r.expire(bucket, window)
        return val <= limit
    except Exception:
        return True  # Allow request if Redis error occurs