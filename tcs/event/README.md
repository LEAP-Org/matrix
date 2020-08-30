# Event-Driven Architecture

The system architecture is starting to get closer to the distributed processing model we desire(see issue #61). However as we have more controllers present in the system, we need more modules to have access to bidirectional communication with the MCU. This can be achieved by passing each distributed processor its own copy of the MCU but greatly increases complexity. 

The solution is to implement an event-driven architecture. Events registered by any module and are bound to an Interrupt Service Routine (ISR). When events are executed their ISRs to which they are registered to get called. This means that any module can execute events and trigger method calls within any module to which it is registered. In addition multiple ISRs from different modules can register to the same event. We group these events by event types.

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
from tcs.event.handler import EventRegistry

class TransmissionControlUnit:
   def __init__(self):
      ...
      with EventRegistry() as event:
         event.register('SESSION_INIT', self.session_init) 

   def session_init(self):
      # execute session init ISR
      ...
```
Then in the `ApHandler` we would simpl make a call to execute the `SESSION_INIT` events which would execute all ISRs that are bound to that event type:
```python
from tcs.event.handler import EventRegistry

class ApHandler:
   def __init__(self):
      ...

   def ap_listener(self):
      ...
      with EventRegistry() as event:
         event.exec('SESSION_INIT', *args, **kwargs)
      ...
```

This is way more scalable since as our interactions between modules grow we won't have to change our modules and test cases as a result of these interactions. Instead the events are handled by the event handler and can be scaled without any additional complexity,

## Best Practices:
1. Modules can only register events to ISRs that they own.
2. All event registration should happen during system initialization to avoid events being executed before being registered.
3. Modules should not contain methods which execute ISRs which are part of the same module.
4. ISRs must be system endpoints which perform standalone actions and do not have a return value
5. Events should not be multi-level: ISRs should not execute other ISRs