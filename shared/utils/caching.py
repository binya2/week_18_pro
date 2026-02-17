import json
import hashlib
import functools
from typing import Callable
from shared.database.redis_connection import redis_manager


def generate_cache_key(func_name: str, *args, **kwargs) -> str:
    clean_args = list(args)
    if clean_args and hasattr(clean_args[0], '__class__') and not isinstance(clean_args[0], (str, int, float, bool)):
        clean_args = clean_args[1:]

    args_repr = f"{clean_args}:{kwargs}"
    args_hash = hashlib.md5(args_repr.encode()).hexdigest()
    return f"cache:{func_name}:{args_hash}"


def cache(expire: int = 60):
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = generate_cache_key(func.__name__, *args, **kwargs)
            redis = redis_manager.get_client()
            try:
                cached_data = await redis.get(cache_key)
                if cached_data:
                    return {
                        "data": json.loads(cached_data),
                        "source": "redis_cache"
                    }
            except Exception as e:
                print(f"Redis read error: {e}")

            result = await func(*args, **kwargs)
            if not result:
                return None
            try:
                if hasattr(result, 'model_dump_json'):
                    data_to_store = result.model_dump_json()
                elif isinstance(result, list) and len(result) > 0 and hasattr(result[0], 'model_dump_json'):
                    data_to_store = json.dumps([item.model_dump() for item in result], default=str)
                else:
                    data_to_store = json.dumps(result, default=str)
                await redis.set(cache_key, data_to_store, ex=expire)
            except Exception as e:
                print(f"Redis write error: {e}")
            return {
                "data": result,
                "source": "mongodb"
            }

        return wrapper

    return decorator
