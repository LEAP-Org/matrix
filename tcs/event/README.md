# Event-Driven Architecture

Modified: 2021-06

The system architecture is starting to get closer to the distributed processing model we desire (see issue #61). However as we have more controllers present in the system, we need more modules to have access to bidirectional communication with the MCU. This can be achieved by passing each distributed processor its own copy of the MCU but greatly increases complexity. 

The solution is to implement an event-driven architecture. Events registered by any module and are bound to some callback function. When events are executed the callbacks to which they are registered are invoked. This means that any module can execute events triggering method calls within any module to which it is registered. In addition multiple ISRs from different modules can register to the same event. We group these events by event types.

## How to use
Below we have an example of the old OO approach:
```python
class ApHandler:
   def __init__(self, tcu):
      self.tcu = tcu
      ...

   def ap_listener(self):
      ...
      self.tcu.session_init()
      ...
```
In order to trigger or access members of the `TransmissionControlUnit` the `ApHandler` would have to be passed a runtime copy of the `tcu` and call its member directly. This gets complicated quickly due to the increased demand for distributed controllers as our system continues to grow.

Here is the same implementation using event-driven architecture:
First in `tcu.py` `__init__` we would register an event to `tcu.session_init`:
```python
from tcs.event.registry import Registry as events

class TransmissionControlUnit:
   def __init__(self):
      ...
      events.session_init.register(self.session_init) 

   def session_init(self):
      # execute session init ISR
      ...
```
Then in the `ApHandler` we would simpl make a call to execute the `SESSION_INIT` events which would execute all ISRs that are bound to that event type:
```python
from tcs.event.registry import Registry as events

class ApHandler:
   def __init__(self):
      ...

   def ap_listener(self):
      ...
      events.session_init.execute(*args, **kwargs)
      ...
```

As our interactions between modules grow the core module logic invocation can remain the same. Instead the events are handled by each event object and can be scaled without any additional complexity.

## Best Practices:
1. Modules can only register events to callbacks that they own.
2. All event registration should happen during system initialization to avoid events being executed before being registered.
3. Modules should not contain methods which execute callbacks which are part of the same module.
4. Callbacks should be asynchronous and return `NoneType`
5. Event IDs should match the name of the event object for clarity during debugging.