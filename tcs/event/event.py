# -*- coding: utf-8 -*-
"""
Events
======
Modified: 2021-06

Dependencies
------------
```
import logging
import asyncio
from typing import Any, Callable, Coroutine, Generic, TypeVar
``` 
Copyright © 2020 LEAP. All Rights Reserved.
"""
import logging
import asyncio
from typing import Any, Callable, Coroutine, Generic, TypeVar

_T = TypeVar('_T', bound=Callable[..., Coroutine[Any, Any, None]])


class Event(Generic[_T]):
    def __init__(self, event_id: str):
        self.log = logging.getLogger(__name__)
        self.event_id = event_id
        self._registry = list()
        self.log.info("%s successfully instantiated", self.event_id)

    def __repr__(self) -> str:
        """
        Event state representation

        :return: representation of event state
        :rtype: str
        """
        return self.event_id + ': ' + str(self._registry)

    def execute(self, *args, **kwargs) -> None:
        """
        Execute asynchronous event queue
        """
        # construct coroutine list and execute
        tasks = [func(*args, **kwargs) for func in self._registry]
        asyncio.run(self._worker(*tasks))

    async def _worker(self, *tasks) -> None:
        """
        Asynchronous dispatcher for event functions. Catch all exceptions and return report
        """
        self.log.info("Dispatched %s", self.event_id)
        results = await asyncio.gather(*tasks, return_exceptions=True)
        # log any exceptions TODO: link exceptions to specific subscriber callbacks
        self.log.info("Event dispatch results: %s", results)

    def register(self, func: _T) -> None:
        """
        Register an async function to this events registry

        :param func: asynchronous endpoint with None rtype
        :type func: _T
        """
        self._registry.append(func)
        self.log.info("Registered event: %s with isr: %s to the registry", self.event_id, func.__name__)
