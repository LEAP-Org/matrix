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

from tcs.file.file_parser import FileParser


class TestFileParser(unittest.TestCase):

    TEST_DIRS = ["samp", "/sampless", "m"]
    CUBE_DIM = 4

    # FIXME: hard to debug since if an error occurs during test cwd is never reset so tearDown
    # and subsequent setUp() functions fail causing the stack trace to be eclipsed.
    def setUp(self):
        # create new directory for files
        os.mkdir("tcs/file/samples")
        self.parser = None

    def tearDown(self):
        # recursively remove directory
        shutil.rmtree("tcs/file/samples")
        del self.parser
    
    def test_extract(self):
        """Sanity test"""
        test_file = open("tcs/file/samples/unittest.txt", "w")
        self.parser = FileParser(self.CUBE_DIM, "samples")
        self.parser.load()
        test_file.close()

    def test_bad_dir(self):
        """Attempt to instantiate a FileParser with an empty or non-existant directory."""
        for test_dir in self.TEST_DIRS:
            with self.subTest(i=test_dir):
                with self.assertRaises(FileNotFoundError):
                    self.parser = FileParser(self.CUBE_DIM, test_dir)
    
    def test_empty_dir(self):
        """Attempt to instantiate by passing an empty or non-existant directory."""
        with self.assertRaises(FileNotFoundError):
            self.parser = FileParser(self.CUBE_DIM, "samples")
    
    def test_bad_filetype(self):
        """Attempt to extract files of a bad type"""
        test_file = open("tcs/file/samples/unittest.yaml", "w")
        with self.assertRaises(TypeError):
            self.parser = FileParser(self.CUBE_DIM, "samples")
        test_file.close()

    def test_bad_arguments(self):
        """Attempt to pass in unexpected argument types"""
        test_file = open("tcs/file/samples/unittest.yaml", "w")
        with self.assertRaises(TypeError):
            self.parser = FileParser([], "samples")
            self.parser = FileParser(5, 3)
        test_file.close()

if __name__ == "__main__":
    unittest.main()
