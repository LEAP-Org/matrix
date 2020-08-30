# -*- coding: utf-8 -*-
"""
Queue Constructor Unittest Suite
================================


Dependencies
------------
>>> import unittest
>>> from bitarray import bitarray
>>> from tcs.controller.queue_constructor import SessionQueue

Copyright © 2020 LEAP. All Rights Reserved.
"""

import unittest

from bitarray import bitarray

from tcs.controller.queue_constructor import SessionQueue


class TestQueueConstructor(unittest.TestCase):

    stringbitarray = """Hey Jason Smith. When are you available? TailorGales is open. Brand new sick ffafa place man. We gotta go check it"""
    stringbitarray2 = """ Ya man I am down. See you tonight at 6PM """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @staticmethod
    def _str_bits(string: str) -> list:
        """Converts a utf-8 string sequence into a series of `bitarray` objects with length of 56.
        
        Args:
        - `string` (`str`): contains a string sequence in utf-8 format.

        Returns:
        - Returns a list of `bitarray` objects of size data_frame_size
        """
        frame_queue = list()
        bit_str = bitarray()
        #compute frame size from the available transmission LEDs divided by 8 bits to convert to bytes
        data_frame_size = int(pow(4,3))
        remainder = len(string)*8 % data_frame_size # remainder in bits
        # convert each byte in string to bit representation of its utf-8 encoding
        for bytex in string:
            bit_str.frombytes(bytes(bytex, 'utf-8'))
            if (len(bit_str)) == data_frame_size:
                frame_queue.append(bit_str)
                bit_str = bitarray()
        # padding remaining bit positions with utf-8 null byte (\x00)
        if remainder != 0:
            for _ in range(data_frame_size-remainder):
                bit_str.append(False)
            frame_queue.append(bit_str)
        return frame_queue

    def test_sanity(self):
        """ Sanity Test """
        reqfiles = [0,1]
        file_dump = [self._str_bits(self.stringbitarray), self._str_bits(self.stringbitarray)] 
        SessionQueue(reqfiles, file_dump)

    def test_init_value_error(self):
        """ Attempt to break initialization case class instantiation of queue constructor for value error """
        #Try passing arguments that are empty
        reqfiles = []
        file_dump = []
        with self.assertRaises(ValueError):
            SessionQueue(reqfiles, file_dump) 

    def test_init_type_error(self):
        """ Attempt to break initialization case class instantiation of queue constructor for type error """
        #Try passing a set for example instead of a list
        reqfiles = {1}
        file_dump = [self._str_bits(self.stringbitarray)]
        with self.assertRaises(TypeError):
            SessionQueue(reqfiles, file_dump)

    def test_init_index_error(self):
        #Try passing reqfiles being less than the file dump
        """ Attempt to break initialization case class instantiation of queue constructor for index error """
        reqfiles = [1,3,5,7]
        file_dump = [1,2,3]
        with self.assertRaises(IndexError):
            SessionQueue(reqfiles, file_dump)    


    def test_next_method(self):   
        """ Check pointer node test """
        #Create an example queue like in the sanity test which works perfectly
        reqfiles = [0,1]
        file_dump = [self._str_bits(self.stringbitarray), self._str_bits(self.stringbitarray)]
        increment_queue_list = SessionQueue(reqfiles, file_dump)
    
        with self.assertRaises(ValueError):
            #Keep iterating until you getting to the end which is a null pointer
            while increment_queue_list is not None:
                increment_queue_list.next()
