# -*- coding: utf-8 -*-
"""
LEAP™ File Parser
=================
Contributors: Steven Zhou, Christian Sargusingh
Date: 2020-02-12
Repository: https://github.com/cSDes1gn/LEAP/tree/master/src/tcs
README available in repository root
Version: 2.0
 
This module continuously parses `utf-8` 7B string segments into binary from all files defined under
the `TRANSMISSION_FILES_DIR` attribute directory. The file data is iteratively appended to a master
list. Each segment only contains data from one file. Therefore, when transitioning to new files, the
current segment is padded with null bytes.
 
Dependencies
------------
>>> import os
>>> from bitarray import bitarray
 
Copyright © 2020 LEAP. All Rights Reserved.
"""
import logging.config
import os
from pathlib import Path

from bitarray import bitarray
from tcs.event.registry import EventRegistry

class FileParser:

    def __init__(self):
        # instantiate logger and set attributes
        self.log = logging.getLogger(__name__)
        payload_dir = os.environ['PAYLOAD_DIR']
        with EventRegistry() as event:
            event.register('FETCH_PAYLOAD', self.load)

        # save current working directory
        cwd = os.getcwd()
        os.chdir(Path(__file__).parent.joinpath(payload_dir))
        self.file_list = os.listdir()
        if not self.file_list:
            self.log.error(
                "Failed to instantiate %s. Verify that there are files listed under: %s",
                __name__, payload_dir)
            # reset working directory on fail
            os.chdir(cwd)
            raise FileNotFoundError

        self.f_paths = [os.path.abspath(x) for x in self.file_list]
        check_ext = list(filter(lambda file : not file.endswith('.txt'), self.f_paths))
        if check_ext:
            self.log.error(
                "Failed to instantiate %s. LEAP only supports transmission of .txt files. Found: %s",
                __name__, str(check_ext))
            # reset working directory on fail
            os.chdir(cwd)
            raise TypeError
        
        # change working directory once path generation complete
        os.chdir(cwd)
        self.file_dir = payload_dir
        self.cube_dim = int(os.environ['DIM'])
        self.log.info("%s successfully instantiated", __name__)
    
    def load(self, ap_index:int):
        """Extracts files under module defined by directory
    
        Args:
        - `cube_dim` (`int`): Size of transmitter for data segmentation calculations.
    
        Returns:
        - (`file_list`, `frame_cnt`, `file_data`) tuple of lists containing file names, number of data
        elements that correspond to each file, and file data as a list of `bitarray` objects.
    
        Raises:
        - OSError: If length of the path list is 0, or error in opening files specified by file paths
        """
        file_data = list()
        frame_cnt=list()
        # main loop to extract data from all files under specified directory
        for path in self.f_paths:
            try:
                file_data.append(
                    self._str_bits(self._file_to_str(path)))
            except OSError as exc:
                self.log.exception("Unable to open file: %s", exc)
                raise OSError from exc
            frame_cnt.append(len(path))
            #TODO: add back framecnt exchange with client
        with EventRegistry() as event:
            event.execute('POST_FRAMECNT', ap_index, sum(frame_cnt))
            event.execute('SESSION_INIT', ap_index, self.file_list, file_data)
    
    def _str_bits(self, string) -> list:
        """Converts a utf-8 string sequence into a series of `bitarray` objects with length of 56.
        
        Args:
        - `string` (`str`): contains a string sequence in utf-8 format.
    
        Returns:
        - Returns a list of `bitarray` objects of size data_frame_size
        """
        frame_queue = list()
        bit_str = bitarray()
        #compute frame size from the available transmission LEDs divided by 8 bits to convert to bytes
        data_frame_size = int(pow(self.cube_dim,3))
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

    @staticmethod
    def _file_to_str(file_path) -> str:
        """Helper method that converts file at specified path into a string sequence.
        
        Args:
        - `file_path` (`str`): contains path of a target file.
    
        Returns:
        - Returns the contents of the file as a string sequence in utf-8 formatting.
        
        Raises:
        - OSError: an internal problem opening the file.
        """
        try:
            transmission_file = open(file_path, "r")
        except OSError:
            raise OSError
        contents = transmission_file.read()
        transmission_file.close()
        return contents
