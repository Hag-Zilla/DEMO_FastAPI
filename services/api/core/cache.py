"""Application caching — fastapi-cache2 setup and shared key builders."""

from typing import Optional

from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend


CACHE_PREFIX = "expense-tracker"


def user_cache_key_builder(
    func,
    namespace: str = "",
    *,
    request=None,
    response=None,
    args=None,
    kwargs=None,
) -> str:
    """Build a per-user cache key.

    Includes the function name, all scalar path/query params, and the current
    user's ID so that users never receive each other's cached results.
    """
    del request, response, args
    kw = kwargs or {}
    # Support both 'current_user' (regular user) and '_admin' (admin-only endpoints)
    user = kw.get("current_user") or kw.get("_admin")
    user_id = getattr(user, "id", "anon")

    # Include only JSON-safe scalars in the key (skip db sessions + ORM objects)
    safe_params = sorted(
        (k, v)
        for k, v in kw.items()
        if isinstance(v, (int, float, str, bool)) and k != "db"
    )

    return f"{CACHE_PREFIX}:{namespace}:{func.__name__}:{safe_params}:uid_{user_id}"


def setup_cache(redis_url: Optional[str] = None) -> None:
    """Initialise FastAPICache with a Redis or in-memory backend.

    Falls back to an in-memory cache when no ``redis_url`` is provided.
    This keeps local development and tests working without a Redis instance.
    """
    if redis_url:
        from redis import asyncio as aioredis  # type: ignore[import]  # pylint: disable=import-outside-toplevel
        from fastapi_cache.backends.redis import RedisBackend  # type: ignore[import]  # pylint: disable=import-outside-toplevel

        redis_client = aioredis.from_url(
            redis_url, encoding="utf8", decode_responses=False
        )
        FastAPICache.init(
            RedisBackend(redis_client),
            prefix=CACHE_PREFIX,
        )
    else:
        FastAPICache.init(InMemoryBackend(), prefix=CACHE_PREFIX)
