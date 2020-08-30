# -*- coding: utf-8 -*-
"""
LEAP™ Access Point Registry
===========================
Contributors: Christian Sargusingh
Updated: 2020-07
Repository: https://github.com/cSDes1gn/LEAP/tree/master/src/tcs
README available in repository root
Version: 1.0
 
Defines a register for TCU to serve active receivers situated at specified access points.
 
This module defines a APRegistry object which holds a session register which stores 
`SessionQueue` objects for active receivers. For TCU runtime, only 1 instance of APRegistry
is active at a time. Therefore it is designed as a Singleton class.
 
Dependencies
------------
>>> from src.tcs.queue_constructor import SessionQueue
 
Copyright © 2020 LEAP. All Rights Reserved.
"""

import logging.config
from tcs.controller.queue_constructor import SessionQueue
from tcs.event.handler import EventHandler
 
class RegisterConstants:
    """Constants class"""
    AP_CAPACITY = 2
 
class APRegistry:
    """Class `APRegistry` defines a register for TCU to serve active receivers situated at
    specified access points.
 
    The session register is defined by its custom `SessionQueue` object active receivers. The
    register entries organized based on transmission cardinal direction: (N,E,S,W). Therefore access
    point 0 would correspond to session register index 0 which is defined as the North direction.
 
    Class Variables:
     - `__instance`: contains instance reference of an instantiated `APRegistry` object.
 
    Attributes:
     - `_sess_reg` (`list`): contains list of active receiver `SessionQueue` objects.
    """
 
    __instance = None
 
    def __init__(self):
        """Initializes session register to None for each cardinal direction.
        
        :raises RuntimeError: If multiple APRegistry objects are instantiated.
        """
        self.log = logging.getLogger(__name__)
        # protect against multiple instances by RuntimeError
        if APRegistry.__instance is not None:
            self.log.error("Class Register is singleton. Cannot call multiple instances.")
            raise RuntimeError
        APRegistry.__instance = self
        # register session events
        with EventHandler() as event:
            event.register('SESSION_INIT', self.insert)
            event.register('SESSION_END', self.remove)
        self._sess_reg = [None, None, None, None]
        self.log.info("%s successfully instantiated", __name__)
 
    def read(self) -> list:
        """Reads private session register field.
 
        Returns:
         - `_sess_reg` (`list`): session register.
        """
        return self._sess_reg
 
    def is_idle(self) -> bool:
        """Validates if the register has no active receivers.
 
        Returns:
         - `True` if session register is empty and `False` otherwise.
        """
        return bool(self._sess_reg == [None,None,None,None])
    
    def max_capacity(self) -> bool:
        """Validates if the register capacity has been reached. Session register capacity is defined
        by `AP_CAPACITY` in `constants` class.
 
        Returns:
         - `True` if the session register is full and `False` otherwise.
        """
        session_queues = 0
        for i in range(len(self._sess_reg)):
            if self._sess_reg[i] is not None:
                session_queues += 1
        return bool(session_queues >= RegisterConstants.AP_CAPACITY)
 
    def insert(self, index:int, file_list:list, file_data:list):
        """
        ISR bound to SESSION_INIT
        :param index: `SessionQueue` insertion index
        :param file_list: list of indices of file_data that correspond to receiver selection
        :param file_data: list of parsed file_data for all available transmission files

        :raises IndexError: If register index contains a `SessionQueue` object or index is out of range
        :raises MemoryError: If session register has reached max capacity.
        :raises ValueError:  If `SessionQueue` instantiation fails.
        """
        self.log.info("Requesting SessionQueue instantiation for AP: %s", index)
        # prevent overwrite of session queue in register
        if self._sess_reg[index] is not None:
            self.log.warning("Restricted overwrite of %s at index %s",self._sess_reg[index], index)
            raise IndexError
        if self.max_capacity():
            self.log.error(
                "Registry at max capacity. Cannot create a new session instance.")
            raise MemoryError
        try:
            self._sess_reg[index] = SessionQueue(file_list,file_data)
        except (ValueError, IndexError, TypeError) as exc:
            self.log.exception(
                "Register write failure. Failed to instantiate SessionQueue object. %s", exc)
            raise ValueError from exc

    def remove(self, index:int):
        """
        ISR bound to SESSION_END 
        :param index: `SessionQueue` deletion index
        """
        # overwrite session queue instance and reassign index position to None
        self._sess_reg[index] = None
        self.log.info("Removed SessionQueue object at index %s", index)
