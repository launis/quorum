from backend_v2.utils.redis_patcher import get_patched_fakeredis_pool


def test_get_patched_fakeredis_pool() -> None:
    pool = get_patched_fakeredis_pool()
    assert pool is not None
