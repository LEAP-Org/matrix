# -*- coding: utf-8 -*-
"""
File Parser Unittest Suite
==========================

Dependencies
------------

Copyright © 2020 LEAP. All Rights Reserved.
"""
import os
import shutil
import unittest
from pathlib import Path
from unittest.mock import Mock

from tcs.event.registry import EventRegistry
from tcs.file.file_parser import FileParser


class TestFileParser(unittest.TestCase):

    TEST_DIRS = ["samp", "/sampless", "m"]
    os.environ['DIM'] = '4'
    os.environ['PAYLOAD_DIR'] = "samples"


    # FIXME: hard to debug since if an error occurs during test cwd is never reset so tearDown
    # and subsequent setUp() functions fail causing the stack trace to be eclipsed.
    def setUp(self):
        EventRegistry.execute = Mock()
        # create new directory for files
        os.mkdir("tcs/file/samples")
        os.environ['PAYLOAD_DIR'] = "samples"
        self.parser = None

    def tearDown(self):
        # recursively remove directory
        shutil.rmtree("tcs/file/samples")
        del self.parser
    
    def test_extract(self):
        """Sanity test"""
        test_file = open("tcs/file/samples/unittest.txt", "w")
        self.parser = FileParser()
        self.parser.load(1)
        test_file.close()

    def test_bad_dir(self):
        """Attempt to instantiate a FileParser with an empty or non-existant directory."""
        for test_dir in self.TEST_DIRS:
            with self.subTest(i=test_dir):
                with self.assertRaises(FileNotFoundError):
                    os.environ['PAYLOAD_DIR'] = test_dir
                    self.parser = FileParser()
    
    def test_empty_dir(self):
        """Attempt to instantiate by passing an empty or non-existant directory."""
        with self.assertRaises(FileNotFoundError):
            self.parser = FileParser()
    
    def test_bad_filetype(self):
        """Attempt to extract files of a bad type"""
        test_file = open("tcs/file/samples/unittest.yaml", "w")
        with self.assertRaises(TypeError):
            self.parser = FileParser()
        test_file.close()

if __name__ == "__main__":
    unittest.main()
