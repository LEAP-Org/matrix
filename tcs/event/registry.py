# -*- coding: utf-8 -*-
"""
Event Registry
==============
Modified: 2021-06

Dependencies
------------
```
from typing import Any, Callable, Coroutine
from tcs.event.event import Event
```
Copyright © 2021 LEAP. All Rights Reserved.
"""

from typing import Any, Callable, Coroutine
from tcs.event.event import Event


class Registry:
    shutdown = Event[Callable[[], Coroutine[Any, Any, None]]]('shutdown')
    transmit = Event[Callable[[bytes], Coroutine[Any, Any, None]]]('transmit')
