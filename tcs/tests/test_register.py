# -*- coding: utf-8 -*-
"""
Receiver Register Unittest Suite
================================

Dependencies
------------


Copyright © 2020 LEAP. All Rights Reserved.
"""
import unittest
from unittest import mock

from tcs.controller.queue_constructor import SessionQueue

from tcs.controller.register import ReceiverRegister, RegisterConstants


class TestRegister(unittest.TestCase):
    """
    Testing buisness logic of the receiver register.
    """

    # create register object (only allowed one invocation per runtime instance)
    register = ReceiverRegister()

    def setUp(self):
        self.mock = mock.MagicMock()

    def tearDown(self):
        # restore register states to None
        self.register._sess_reg = [None, None, None, None]
        # remove mock
        del self.mock
    
    def test_singleton(self):
        """Try and instantiate duplicate registers in the same runtime environment"""
        with self.assertRaises(RuntimeError):
            _ = ReceiverRegister()

    def test_is_idle(self):
        """Test the idle state method for all register configurations"""
        self.register._sess_reg = [self.mock, self.mock, self.mock,self.mock]
        assert not self.register.is_idle()
        self.register._sess_reg = [None, None, None, None]
        assert self.register.is_idle()
        self.register._sess_reg = [None, None, None, self.mock]
        assert not self.register.is_idle()

    def test_max_capacity(self):
        """Test the boolean response for the register capacity according to its set values"""
        assert RegisterConstants.AP_CAPACITY > 0
        # testing upper limits
        for i in range(RegisterConstants.AP_CAPACITY):
            self.register._sess_reg[i] = self.mock
        assert self.register.max_capacity()
        # testing lower limits
        self.register._sess_reg = [None, None, None, None]
        assert not self.register.max_capacity()

    def test_write(self):
        """Test the register writing functionality."""
        self.register.write(0, [0, 1], ["0101010", "10010101"])
        assert isinstance(self.register.read()[0], SessionQueue)

    def test_write_over_max(self):
        """Attempt to write to the register over the maximum allowed capacity."""
        # if the AP_CAPACITY is at 4 then the overwrite raise will always occur first
        if RegisterConstants.AP_CAPACITY != 4:
            assert RegisterConstants.AP_CAPACITY > 0
            # Reaching upper capactiy limits
            for i in range(RegisterConstants.AP_CAPACITY):
                self.register._sess_reg[i] = self.mock
            with self.assertRaises(MemoryError):
                self.register.write(3, ["file1.txt", "file2.txt"], ["0101010", "10010101"])

    def test_delete(self):
        """Verify the write() function removes object at index replacing it with NoneType"""
        self.register._sess_reg = [self.mock, self.mock, self.mock, self.mock]
        self.register.write(3)
        assert self.register.read()[3] is None
        self.register.write(1)
        assert self.register.read()[1] is None

    def test_overwrite(self):
        """Attempt to overwrite active access point session queue obj"""
        self.register._sess_reg = [self.mock, None, None, None]
        with self.assertRaises(IndexError):
            self.register.write(0, [], [])

if __name__ == "__main__":
    unittest.main()
