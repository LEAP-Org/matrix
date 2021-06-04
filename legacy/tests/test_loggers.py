# -*- coding: utf-8 -*-
"""
Logging Unittest Suite
======================
Tests validating the functionality of each module logger.

Dependencies
------------
>>> import hashlib
>>> import logging.config
>>> import os
>>> import unittest
>>> from pathlib import Path

>>> import yaml

>>> from tcs.logs.config import log_config
>>> from rcs.logs.config import log_config

Copyright © 2020 LEAP. All Rights Reserved.
"""

import hashlib
import logging.config
import unittest
from pathlib import Path

import yaml


class TestTCSLoggers(unittest.TestCase):
    # intialize loggers

    log_paths = {
        '': "tcs/logs/root.log",
        'tcs.tcu.tcu': "tcs/logs/tcu.log",
        'tcs.tcu.queue_constructor': "tcs/logs/queue.log",
        'tcs.file.file_parser': "tcs/logs/file_parser.log",
        'tcs.tcu.registry': "tcs/logs/registry.log",
        'tcs.codec.spatial_codec': "tcs/logs/spatial_codec.log",
        'tcs.codec.cache': "tcs/logs/cache.log",
        'tcs.event':"tcs/logs/event.log"
    }
    tcs_config_path = Path("tcs/logs/config/config.yaml")

    def setUp(self):
        from tcs.logs.config import log_config

    def tearDown(self):
        pass

    @staticmethod
    def md5(filename: str) -> str:
        """"Helper to hash a file for fast file comparison"""
        # using md5 for speed
        _hash = hashlib.md5()
        # open file for reading in binary mode
        with open(filename,'rb') as file:
            for block in iter(lambda: file.read(1024), b""):
                _hash.update(block)
        return _hash.hexdigest()

    def test_config_load(self):
        with open(self.tcs_config_path) as file:
            _ = yaml.full_load(file)

    def test_fp_logger(self):
        """Verify logger for FileParser is functional"""
        log_path = self.log_paths['tcs.file.file_parser']
        log = logging.getLogger('tcs.file.file_parser')
        ctrl = self.md5(log_path)
        log.debug("test")
        assert self.md5(log_path) != ctrl

    def test_cache_logger(self):
        """Verify logger for Cache is functional"""
        log_path = self.log_paths['tcs.codec.cache']
        log = logging.getLogger('tcs.codec.cache')
        ctrl = self.md5(log_path)
        log.debug("test")
        assert self.md5(log_path) != ctrl

    def test_qc_logger(self):
        """Verify logger for SessionQueue is functional"""
        log_path = self.log_paths['tcs.tcu.queue_constructor']
        log = logging.getLogger('tcs.tcu.queue_constructor')
        ctrl = self.md5(log_path)
        log.debug("test")
        assert self.md5(log_path) != ctrl
    
    def test_register_logger(self):
        """Verify logger for Register is functional"""
        log_path = self.log_paths['tcs.tcu.registry']
        log = logging.getLogger('tcs.tcu.registry')
        ctrl = self.md5(log_path)
        log.debug("test")
        assert self.md5(log_path) != ctrl
    
    def test_tcu_logger(self):
        """Verify logger for TCU is functional"""
        log_path = self.log_paths['tcs.tcu.tcu']
        log = logging.getLogger('tcs.tcu.tcu')
        ctrl = self.md5(log_path)
        log.debug("test")
        assert self.md5(log_path) != ctrl
        
    def test_sc_logger(self):
        """Verify logger for SpatialCodec is functional"""
        log_path = self.log_paths['tcs.codec.spatial_codec']
        log = logging.getLogger('tcs.codec.spatial_codec')
        ctrl = self.md5(log_path)
        log.debug("test")
        assert self.md5(log_path) != ctrl

    def test_e_logger(self):
        """Verify logger for FileParser is functional"""
        log_path = self.log_paths['tcs.event']
        log = logging.getLogger('tcs.event')
        ctrl = self.md5(log_path)
        log.debug("test")
        assert self.md5(log_path) != ctrl
    
    def test_root_logger(self):
        """Verify root logger for unregistered module signatures are functional"""
        # root logs are Stream handled
        # log_path = self.log_paths['']
        # log = logging.getLogger('df')
        # ctrl = self.md5(log_path)
        # log.debug("test")
        # assert self.md5(log_path) != ctrl
    
if __name__ == "__main__":
    unittest.main()
