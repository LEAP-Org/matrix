# -*- coding: utf-8 -*-
"""
Event Handler Unittest Suite
============================

Dependencies
------------
>>> import unittest
>>> from unittest.mock import Mock
>>> from tcs.event.registry import EventRegistry
>>> from tcs.event.event import Event

Copyright © 2020 LEAP. All Rights Reserved.
"""
import unittest
from unittest.mock import Mock
from tcs.event.registry import EventRegistry
from tcs.event.event import Event

class TestEvents(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        """ Remove test events from the registry """
        with EventRegistry() as event:
            try:
                event._event_registry.pop('TEST_EVENT')
            except KeyError:
                pass
            try:
                event._event_registry.pop('SECONDARY_EVENT')
            except KeyError:
                pass

    def test_isr_type(self):
        """ Attempt to create an event with an uncallable callback """
        bad_isrs = [4, None, 'string']
        for isr in bad_isrs:
            with self.subTest(name=isr):
                with self.assertRaises(TypeError):
                    _ = Event('TEST_EVENT', isr)

    def test_bad_register(self):
        """ Attempt to register an event with a bad type"""
        with EventRegistry() as event:
            event.register('TEST_EVENT', 1)
            self.assertEqual(len(event._event_registry),0)
    
    def test_register(self):
        """ Verify functionality of event registeration """
        with EventRegistry() as event:
            isr = Mock(return_value=None)
            event.register('TEST_EVENT', isr)
            self.assertEqual(len(event._event_registry),1)
            self.assertTrue(isinstance(event._event_registry['TEST_EVENT'],set))
            self.assertTrue(next(iter(event._event_registry['TEST_EVENT'])).isr is isr)

    def test_set_event_mask(self):
        """ Verify the functionality of the event masking """
        isr1, isr2, isr3 = Mock(), Mock(), Mock()
        with EventRegistry() as event:
            event.register('TEST_EVENT', isr1)
            event.register('TEST_EVENT', isr2)
            event.register('SECONDARY_EVENT', isr3)
        with EventRegistry() as event:
            event.set_mask('TEST_EVENT', True)
            unmasked = list(
                filter( lambda e : e.masked==False, event._event_registry['TEST_EVENT'])
            )
        self.assertTrue(len(unmasked) == 0)

    def test_execute(self):
        """ Verify the functionality of the event execution """
        isr1, isr2, isr3 = Mock(), Mock(), Mock()
        with EventRegistry() as event:
            event.register('TEST_EVENT', isr1)
            event.register('TEST_EVENT', isr2)
            event.register('SECONDARY_EVENT', isr3)
        param = Mock()
        with EventRegistry() as event:
            event.execute('TEST_EVENT', param)
        isr1.assert_called_once_with(param)
        isr2.assert_called_once_with(param)
        self.assertTrue(isr3.call_count == 0)

    def test_masked_execute(self):
        """ Verify the functionality of masked event execution """
        isr1, isr2 = Mock(), Mock()
        with EventRegistry() as event:
            event.register('TEST_EVENT', isr1)
            event.register('TEST_EVENT', isr2)
        with EventRegistry() as event:
            event.set_mask('TEST_EVENT', True)
        param = Mock()
        with EventRegistry() as event:
            event.execute('TEST_EVENT', param)
        self.assertTrue(isr1.call_count == 0)
        self.assertTrue(isr2.call_count == 0)

if __name__ == "__main__":
    unittest.main()