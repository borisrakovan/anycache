import asyncio
import functools
import hashlib
import inspect
import logging
from pathlib import Path
from typing import Callable, ParamSpec, TypeVar, overload, Any

from anycache.serializers import Serializer, PickleSerializer

logger = logging.getLogger(__name__)


class CacheWrapper:
    """Decorator for caching function results to file based on an arbitrary key"""

    def __init__(
        self,
        cache_dir: str | Path,
        namespace: str | None = None,
        is_method: bool = False,
        serializer: Serializer | None = None,
    ):
        self.is_method = is_method

        if not isinstance(cache_dir, Path):
            cache_dir = Path(cache_dir)

        if namespace is not None and (parts := namespace.split(".")):
            cache_dir = cache_dir.joinpath(*parts)

        cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir = cache_dir
        self.serializer = serializer or PickleSerializer()

    def read(self, func, args, kwargs) -> Any:
        key = self.make_key(func.__name__, args, kwargs)

        if not (cache_file := self.cache_dir / key).exists():
            return None

        try:
            with cache_file.open("rb") as f:
                content = self.serializer.loads(f.read())
        except Exception as exc:
            # Remove the cache file if it's corrupted
            cache_file.unlink()
            logger.warning(f"Failed to read a corrupted file from cache: {str(exc)}")
            return None

        logger.info(f"Resource {key} loaded from cache")
        return content

    def write(self, content, func, args, kwargs) -> None:
        key = self.make_key(func.__name__, args, kwargs)

        try:
            with (cache_file := self.cache_dir / key).open(mode="wb") as f:
                f.write(self.serializer.dumps(content))
            logger.info(f"Resource {key} saved to cache")
        except Exception as exc:
            # Remove the cache file if it's corrupted
            cache_file.unlink()
            logger.info(f"Failed to write to cache: {str(exc)}")

    def make_key(self, func_name, args, kwargs) -> str:
        """
        Create a unique key for a function call.
        Each function call is uniquely identified by its name and the arguments it was called with.
        """

        # Ignore the self argument of a method
        args = args[1:] if self.is_method else args
        key_parts = [
            func_name,
            "_".join(str(arg) for arg in args),
            "_".join(f"{k}={v}" for k, v in sorted(kwargs.items())),
        ]

        string = ":".join(kp for kp in key_parts if kp)
        return hashlib.sha256(string.encode("utf-8")).hexdigest()

    def sync_wrapper(self, func, *args, **kwargs):
        """Wrapper for sync functions"""
        if (hit := self.read(func, args, kwargs)) is not None:
            return hit

        content = func(*args, **kwargs)
        self.write(content, func, args, kwargs)
        return content

    def sync_gen_wrapper(self, func, *args, **kwargs):
        """Wrapper for sync generators"""
        if (hit := self.read(func, args, kwargs)) is not None:
            yield from hit

        else:
            content = []
            for item in func(*args, **kwargs):
                content.append(item)
                yield item

            self.write(content, func, args, kwargs)

    async def async_wrapper(self, func, *args, **kwargs):
        """Wrapper for async functions"""
        if (hit := self.read(func, args, kwargs)) is not None:
            return hit

        content = await func(*args, **kwargs)
        self.write(content, func, args, kwargs)
        return content

    async def async_gen_wrapper(self, func, *args, **kwargs):
        """Wrapper for async generators"""
        if (hit := self.read(func, args, kwargs)) is not None:
            for item in hit:
                yield item
        else:
            content = []
            async for item in func(*args, **kwargs):
                content.append(item)
                yield item
            self.write(content, func, args, kwargs)

    def __call__(self, func):
        """Create async or sync wrapper based on the type of the wrapped function"""

        if asyncio.iscoroutinefunction(func):
            wrapper = self.async_wrapper
        elif inspect.isasyncgenfunction(func):
            wrapper = self.async_gen_wrapper
        elif inspect.isgeneratorfunction(func):
            wrapper = self.sync_gen_wrapper
        else:
            wrapper = self.sync_wrapper

        def wrapped(*args, **kwargs):
            return wrapper(func, *args, **kwargs)

        return wrapped


P = ParamSpec("P")
R = TypeVar("R")


@overload
def cache(__fn: Callable[P, R]) -> Callable[P, R]:
    ...


@overload
def cache(
    *, cache_dir: str | None = None, namespace: str | None = None, is_method: bool = False
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    ...


def cache(
    fn: Callable[P, R] | None = None,
    *,
    cache_dir: str | None = None,
    namespace: str | None = None,
    is_method: bool = False,
    serializer: Serializer | None = None,
):
    """Decorator that caches the result of a function call based on its unique arguments"""
    if not fn:
        # Allow using decorator with or without parentheses
        # i.e. @file_cache(namespace=a.b.c) or just @file_cache
        return functools.partial(cache, cache_dir=cache_dir, namespace=namespace, is_method=is_method)

    return CacheWrapper(cache_dir, namespace, is_method, serializer)(fn)
