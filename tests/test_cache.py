import asyncio
import tempfile

import pytest

from anycache import cache


def test_cache_sync_func():

    with tempfile.TemporaryDirectory() as tmpdir:
        n_calls = 0

        @cache(cache_dir=tmpdir)
        def fn(a: int):
            nonlocal n_calls
            n_calls += 1
            return a + 1

        assert fn(3) == 4
        assert fn(3) == 4
        assert n_calls == 1


@pytest.mark.asyncio
async def test_cache_async_func():
    with tempfile.TemporaryDirectory() as tmpdir:
        n_calls = 0

        @cache(cache_dir=tmpdir)
        async def fn(a: int):
            await asyncio.sleep(0)
            nonlocal n_calls
            n_calls += 1
            return a + 1

        assert await fn(3) == 4
        assert await fn(3) == 4
        assert n_calls == 1


def test_cache_sync_gen():

    with tempfile.TemporaryDirectory() as tmpdir:
        n_calls = 0

        @cache(cache_dir=tmpdir)
        def fn(a: int):
            nonlocal n_calls
            n_calls += 1

            for i in range(3):
                yield a + i

        assert list(fn(3)) == [3, 4, 5]
        assert list(fn(3)) == [3, 4, 5]
        assert n_calls == 1


@pytest.mark.asyncio
async def test_cache_async_gen():

    with tempfile.TemporaryDirectory() as tmpdir:
        n_calls = 0

        @cache(cache_dir=tmpdir)
        async def fn(a: int):
            await asyncio.sleep(0)
            nonlocal n_calls
            n_calls += 1

            for i in range(3):
                yield a + i

        assert [x async for x in fn(3)] == [3, 4, 5]
        assert [x async for x in fn(3)] == [3, 4, 5]
        assert n_calls == 1
