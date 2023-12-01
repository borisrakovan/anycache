import base64
import pickle
from typing import Protocol, Any


class Serializer(Protocol):
    def dumps(self, obj: Any) -> bytes:
        ...

    def loads(self, blob: bytes) -> Any:
        ...


class PickleSerializer:
    def dumps(self, obj: Any) -> bytes:
        blob = pickle.dumps(obj)
        return base64.encodebytes(blob)

    def loads(self, blob: bytes) -> Any:
        return pickle.loads(base64.decodebytes(blob))