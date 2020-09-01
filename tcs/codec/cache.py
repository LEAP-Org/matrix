# -*- coding: utf-8 -*-
"""
LEAP™ TransmissionCache
=======================
Contributors: Christian Sargusingh
Date: 2020-06-06
Repository: https://github.com/cSDes1gn/LEAP/tree/master/src/tcs
README available in repository root
Version: 

Class `TransmissionCache` defines a LIFO caching architecture saving a history of transmitted
frame data. This class also provides the spatial encoding and subsequent hardware mapping
required to send to the arduino microcontroller. As the TCU processes a transmission request,
it calls `cache_map()` sending it the raw binary frame data and the transmission direction
(access point). The `cache_map()` function uses our `SpatialCodec` object to determine the 
encoded mapping for all access points and updates the cache with the new frame data. The
corresponding binary hardware mapping is returned to the TCU to send to the arduino serial
monitor. The `check()` function is used to verify APR codes with the contents of the
transmitter cache.

Dependencies
------------
>>> import logging.config
>>> import bitarray
>>> import numpy as np
>>> from tcs.codec.spatial_codec import SpatialCodec
 
Copyright © 2020 LEAP. All Rights Reserved.
"""
import logging.config

import bitarray
import numpy as np
import math

from tcs.codec.spatial_codec import SpatialCodec
from tcs.event.registry import EventRegistry


class constants:
    CACHE_SIZE = 10
    # Hardware mapping for LEAP™ v2 hardware
    # Bottom Layer 0    Middle Layer 1    Middle Layer 2    Top Layer 3
    # --------------    --------------    --------------    -----------
    # 12 13 14 15       28 29 30 31       44 45 46 47       60 61 62 63
    # 8  9  10 11       24 25 26 27       40 41 42 43       56 57 58 59
    # 4  5  6  7        20 21 22 23       36 37 38 39       52 53 54 55
    # 0  1  2  3        16 17 18 19       32 33 34 35       48 49 50 51
    HM = np.array([
        [[12,13,14,15],[8,9,10,11],[4,5,6,7],[0,1,2,3]],
        [[28,29,30,31],[24,25,26,27],[20,21,22,23],[16,17,18,19]],
        [[44,45,46,47],[40,41,42,43],[36,37,38,39],[32,33,34,35]],
        [[60,61,62,63],[56,57,58,59],[52,53,54,55],[48,49,50,51]]
    ])
    # Hardware Map for 2x2x2 LED Cube
    HM2 = np.array([[[2,3],[0,1]],[[6,7],[4,5]]])
    AP = 4

class TransmissionCache:
    """
    Attributes:
     - `_cache` (`list`): list of cached frame data 4 slots wide for each transmission direction.
     - `_spatial_codec` (`SpatialCodec`): TCU spatial encoder object
    """

    def __init__(self, cube_dim: int):
        """Initializes empty list for cached frames and stores a reference to the `SpatialCodec`
        object instantiated by the TCU.
        """
        self.log = logging.getLogger(__name__)
        if cube_dim < 0 or math.ceil(np.log2(cube_dim)) != np.log2(cube_dim):
            self.log.error(
                "Received unexpected cube dimension size. Cube dimension must be a power of 2.")
            raise ValueError
        self._spatial_codec = SpatialCodec(cube_dim, constants.HM)
        self._cache = list()
        with EventRegistry() as event:
            event.register('VALIDATE_APR', self.validate)
        self.log.info("%s successfully instantiated", __name__)
 
    def cache_map(self, bin_frame: bitarray, ap_index: int) -> bitarray:
        """This function uses TCU instantiated `SpatialCodec` to perform 3 operations. First,
        the binary input data is encoded into its corresponding spatial map for the requested
        access point. Second, the spatial map is converted into a binary hardware map to send to the
        arduino microcontroller based on its corresponding pinouts specified in the `constants` 
        class. Lastly, the frame is decoded for all 4 access points and updated as a cache entry. 
        The purpose is to store a list of entries that a verified receiver would decode and used to
        identify the position of the receiver.
 
        Args:
         - `bin_frame` (`bitarray`): raw binary frame data to be encoded and mapped to the hardware
         - `ap_index` (`int`): index for access point (direction) encoding 0 > N proceeding
         clockwise.
 
        Returns:
         - `encoded_frame` (`bitarray`): binary hardware map based on the transmitters hardware map
        (pinouts) specified in `constants.HM`.
        """
        if len(self._cache) == constants.CACHE_SIZE:
            self._cache.pop(0)   # pop the bottom of the cache
        cache_entry = list()
        # determine the decoded frame data of all access points 
        for i in range(constants.AP):
            frame = self._spatial_codec.encode(bin_frame,i)
            if i == ap_index:
                encoded_frame = self._spatial_codec.hardware_map(frame)
            cache_entry.append(self._spatial_codec.decode(frame))
        self._cache.append(cache_entry)
        return encoded_frame
    
    def validate(self, apr: bitarray):
        """
        This function is an ISR bound to event:VALIDATE_APR. It references the cache and compares 
        the apr code sent by a receiver for access point validation to find a match. If a match is 
        found the APR_VALIDATED event is triggered with the index

        :param apr: decoded frame data cached by a receiver during calibration
        :returns:
        """
        # FIXME: If cache is a dict based approach the retrieval time is significantly faster
        with EventRegistry() as event:
            for i in range(len(self._cache)):
                for j in range(len(self._cache[i])):
                    if apr == self._cache[i][j]:
                        event.execute('APR_VALIDATED', j)
                        self.log.info("Validated APR key: %s", apr)
                        return
            self.log.info("Revoked APR key: %s", apr)
            event.execute('POST_REQUEST', False, "Access Point Registry invalid. Request declined.")
