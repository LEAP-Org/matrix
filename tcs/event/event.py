# -*- coding: utf-8 -*-
"""
LEAP™ Events
============
Contributors: Christian Sargusingh
Modified: 2020-07
Repository: https://github.com/LEAP-Org/LEAP
README available in repository root
Version: 1.0

Dependencies
------------

Copyright © 2020 LEAP. All Rights Reserved.
"""
import logging.config

class Event:

    def __init__(self, event_type: str, isr):
        """
        :raises TypeError: if isr is not callable
        """
        self.log = logging.getLogger(__name__)
        self.masked = False
        self._type = event_type
        if not callable(isr):
            raise TypeError
        self.isr = isr
        self.log.info("Created event: %s", self)

    def set_mask(self, state: bool):
        """ Set the mask of this Event """
        self.masked = state