# -*- coding: utf-8 -*-
"""
LEAP™ Transmission Control Unit
===============================
Modified: 2021-06

Dependancies
------------
```
import logging
import hashlib

from cacheout import FIFOCache
```
Copyright © 2021 LEAP. All Rights Reserved.
"""
import logging
import hashlib

from cacheout import FIFOCache


class FrameCache:

    _cache = FIFOCache(maxsize=256, ttl=10)

    def __init__(self) -> None:
        self._log = logging.getLogger(__name__)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        pass

    def post(self, bytestream: bytes) -> None:
        # apply md5 hash to bytestream and save to cache for lookup
        md5_digest = hashlib.md5(bytestream).hexdigest()
        self._log.info("computed md5 digest: %s -> %s", bytestream, md5_digest)
        # set frame to fifo cache
        ap = 0  # TODO: add multidirectional access point cache
        self._cache.set(md5_digest, ap)
        self._log.info("set frame to cache")

    def get(self, md5_digest: str) -> bool:
        result = self._cache.get(md5_digest)
        if result is None:
            self._log.info("cache digest: %s expired or does not exist.", md5_digest)
            return False
        # autoclear discovered element
        self._cache.delete(md5_digest)
        self._log.info("cache digest: %s discovered at access point: %s and removed.", md5_digest, result)
        return True

    def clear(self) -> None:
        self._cache.clear()
