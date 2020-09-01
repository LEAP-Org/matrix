# -*- coding: utf-8 -*-
"""
LEAP™ Event Registry
===================
Contributors: Christian Sargusingh
Modified: 2020-07
Repository: https://github.com/LEAP-Org/LEAP
README available in repository root
Version: 1.0

Event control module

Dependencies
------------
 
Copyright © 2020 LEAP. All Rights Reserved.
"""
import sys
import logging.config
from threading import Thread
from tcs.event.event import Event

class EventRegistry:
    """
    Visual representation of event registry
    {   'event_type': {<Event@1082>, <Event@1f4e>, <Event@43ab>}
        'event_type': {}
        ... 
    }
    """
    
    _event_registry = dict()

    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.log.info("%s successfully instantiated", __name__)

    def __enter__(self):
        caller_id = sys._getframe().f_back.f_code.co_name
        self.log.info("Event Handler entered from: %s", caller_id)
        return self

    def __exit__(self, type, value, traceback):
        pass

    def __repr__(self):
        return str(self._event_registry)

    def set_mask(self, event_type: str, state:bool):
        """ Set the mask field of a set of events """
        try:
            events = self._event_registry[event_type]
        except KeyError:
            self.log.error("Event type does not exist in registry")
        else:
            for event in events:
                event.set_mask(state)

    def execute(self, event_type: str, *args, **kwargs):
        """
        Dispatches a new thread for each ISR bound to te triggered event_type. This method filters by
        events that are not masked
        :param event_type: execute all isr's bound to this event type
        """
        try:
            events = filter(lambda event : not event.masked, self._event_registry[event_type])
        except KeyError:
            self.log.error("Event type does not exist in registry")
        else:
            for event in events:
                event.isr(args,kwargs)
            self.log.info("Successfully dispatched all events for %s", event_type)
        self.log.info(self)

    def register(self, event_type: str, isr):
        """
        Creates and registers new ISRs into the event registry and binds them to event type keys 
        :param event_type: key defining the execution of a grouped events
        :param isr: interrupt service routine
        """
        try:
            event = Event(event_type, isr)
        except TypeError as exc:
            self.log.exception("Event could not be created due to an unexpected type: %s", exc)
        else:
            try:
                self._event_registry[event_type].add(event)
            except KeyError:
                # create an empty queue if event type is not in the registry
                self._event_registry[event_type] = {event}
            self.log.info("Registered event: %s with isr: %s to the registry", event, event.isr)
        self.log.info(self)
        