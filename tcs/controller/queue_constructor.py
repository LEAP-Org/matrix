# -*- coding: utf-8 -*-
"""
LEAP™ Queue Constructor
=======================
Contributors: Christian Sargusingh
Date: 2019-11-20
Repository: https://github.com/cSDes1gn/LEAP/tree/master/src/tcs
README available in repository root
Version: 1.0
 
Queue Constructor creates custom linked lists containing user requested transmission frames.
The `SessionQueue` object points to the next frame element in the linked list.
SessionQueue objects are instantiated and stored into a register by the TCU when a new receiver
establishes a connection to an access point on the transmitter.
 
Copyright © 2020 LEAP. All Rights Reserved.
"""

import logging.config
 
class Node:
    """Node class defines node objects linked lists.
 
    Attributes:
     - `data` (`bitarray`): holds one frame (7B) worth of file data.
     - `next` (`ref`): points to the next node in a set of nodes
    """
    
    def __init__(self, data): 
        self.data = data 
        self.next = None
 
class SessionQueue:
    """Class `SessionQueue` creates a custom transmission frame queue using a linked list.
 
    The transmitter creates a custom `SessionQueue` object for the files requested building a singly
    linked-list. Each node of the linked list holds a frame of sequential `bitarray` transmission
    data. `SessionQueue` objects provide a next() function to traverse through the linked list 
    reading each frame of data for the active user. When next() reaches the end of the linked list
    it raises ValueError which notifies the TCU the user data request has been satisfied. The TCU
    then destroys this instance of `SessionQueue`.
 
    Attributes:
     - _req (`list`): `_file_list` contains names of requested files.
     - _frame_data (`list`): `_frame_data` contains data frames of requested files
     - _head (`node`): `_frame_data` contains data frames of requested files
    """
 
    def __init__(self, req_files: list, file_dump: list):
        """Constructor for SessionQueue objects.
 
        Args:
         - `req_files`(`list`): contains names of requested files.
         - `file_dump` (`list`): is a list of `bitarray` lists of requested file data
 
        Raises:
         - ValueError: Raised if no files are requested (file_list attribute empty)
         - IndexError: Raised if the frame_data and file_list indices do not match.
         - TypeError: Raised if input parameters are not lists.
        """
        self.log = logging.getLogger(__name__)

        if len(req_files) < 1:
            raise ValueError("No files submitted for Queue.")
        
        if len(req_files) != len(file_dump):
            raise IndexError("Mis-alignment of file list index to data frame index.")
 
        # file_list and frame_data fields private and immutable. Filename indices correspond with 
        # frame data indices.
        self._req_files = req_files
        self._head = None
 
        self._frame_data = list()
        #modify _frame_data to correspond to requested files
        for i in range(len(self._req_files)):
            self._frame_data.append(file_dump[self._req_files[i]])
 
        #build linked list from the last elem to first to start head at first indice
        for i in reversed(range(len(self._frame_data))):
            for j in reversed(range(len(self._frame_data[i]))):
                new_node = Node(self._frame_data[i][j]) 
                new_node.next = self._head
                self._head = new_node
        self.log.info("%s successfully instantiated", __name__)

    def next(self):
        """Returns the current node and increments the pointer to the next node.
 
        Raises:
         - ValueError: If head node points to null signifying linked list traverse finished.
 
        Returns:
         - Node contents (bitarray holding 7B of data) pointed to by _head pointer
        """
        if self._head is None:
            self.log.info("Reached end of SessionQueue")
            raise ValueError
        
        current = self._head
        self._head = current.next
        self.log.info("Incremented frame pointer")
        return current.data
        