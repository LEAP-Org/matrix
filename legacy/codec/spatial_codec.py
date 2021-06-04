# -*- coding: utf-8 -*-
"""
Spatial Codec™
==============
Contributors: Christian Sargusingh
Date: 2020-02-14
Repository: Condensed solution based on https://github.com/cSDes1gn/spatial-codec
README available in repository root
Version: v2.0T Derived from v2.0
 
Spatial Codec™ is a specialized spatial encoding and decoding algorithm developed for mapping a 1D 
bitmap to a 3D matrix with a specified voxel (3D pixel) resolution. The encoder takes a 1D 
bitarray and translates the bit pattern to an equivalent spatial map using a 3D matrix with 
specified resolution.
 
The spatial encoder maps according to Hilbert's space filling curve (HSFC)
(https://en.wikipedia.org/wiki/Hilbert_curve) which preserves localized bits in 1D to geometry in 3D
space independent of the matrix dimension. The encoder generates a Frame object which comprises of a
3D matrix with bits mapped according to Hilbert's space filling curve. The spatial decoder takes a 
Frame object and matrix element multiplication to find a reduced index matrix in order to 
reconstruct the 1D bitarray index mapping.

Dependencies
------------
>>> import numpy as np
>>> from bitarray import bitarray

Copyright © 2020 LEAP. All Rights Reserved.
"""
 
import logging.config
import numpy as np
from bitarray import bitarray
 

class bcolors:
    """Class defining escape sequences for terminal color printing"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
 
class Frame:
    """Class `Frame` represents a 1D bitmap as a 3D spatial map of specified size.
 
    `Frame` is a wrapper for an encoded 3D spatially encoded bitarray index map. For clarity we 
    refer to this as a spatial map. This object provides controlled get and set definitions for
    manipulating the spatial map matrix contents.
 
    Attributes:
     - `_spatial_map` (`np.matrix`): is a 3D matrix of integers.
    """
    def __init__(self, cube_dim):
        """Constructor for `Frame` objects
 
        Args:
         - `cube_dim` (`int`): cube dimension of LED transmitter.
        """
        self._spatial_map = np.zeros((cube_dim,cube_dim,cube_dim), dtype=int)
 
    def read(self):
        """Returns a spatial map matrix defined by this instance of `Frame`.
 
        Returns:
         - Returns the `_spatial_map` matrix.
        """
        return self._spatial_map
 
    def write(self, x_in, y_in, z_in, bit=1):
        """Writes a bit to the spatial map matrix within this instance of `Frame`. If the `bit`
        parameter is undefined assume '1' bit write.
 
 
        Args:
         - `x_in` (`int`): x index
         - `y_in` (`int`): y index
         - `z_in` (`int`): z index
         - `bit` (`int`): bit value (1 by default)
        """
        self._spatial_map[x_in][y_in][z_in] = bit
 
class SpatialCodec:
    """Class `SpatialCodec` defines the codec for spatial encoding and decoding based on Hilbert's 
    space filling curve algorithm.
 
    `SpatialCodec` has two primary definitions `encode()` and `decode()` for converting `bitarray`
    objects into `Frame` objects and vice-versa. `remap()` and `hardware_map()` definitions 
    specifically designed for the TCU module. These are protected definitions that are only provided
    with version 2.0T. This allows the TCU to encode and map frame data to the transmitter for all 
    access points. The receiving unit will always decode the frame according to a standardized 
    method.
 
    Attributes:
     - `dim` (`int`): defines the cube dimension of the transmitter
     - _h_curve (`np.matrix`): Holds `bitarray` index numbers in a 3D matrix defined by HSFC
     - `ant_d` (`np.matrix`): defines a 2D anti-diagonal identity matrix
     - `bit_index` (`int`): is a temporary attribute used to hold the running bit index count for
     `hilberts_curve()`
     - `_spatial_maps` (`list`): memory for all translated versions of the hilbert curve spatial map
     - `_hml` (`np.matrix`): 1D bitmap conversion of 3D hardware spatial map parameter defined by 
     TCU module.
     - `pseudo_bits` (`list`): hardcoded bitmap indices with a constant bit value of 0.
    """
    def __init__(self, dim, h_map):
        """Initializes empty `_h_curve` by generating a spatial map using `hilbert_curve()`. Defines
        anti-diagonal identity matrix `ant_d` for `remap()` definition responsible for spatial map
        transformations. Uses h_curve and `remap()` to construct a master list of all spatial map
        transformations. Generates a 1D bitmapping of the input 3D hardware spatial map.
 
        Args:
         - `dim` (`int`): is the dimension of the 3D matrix.
         - `h_map` (`np.matrix`): 3D hardware spatial map defined by TCU module. 
        
        Raises:
         - `ValueError`: Raised if the parameter `dim` is not a power of 2. Restriction by HSFC 
          algorithm
        """
        self.log = logging.getLogger(__name__)
        self.dim = dim
        self.bit_index = 0  # defined as an attribute for tracking recursion completion
 
        # entry check to hilberts_curve to ensure dim parameter is a power of 2
        if np.log2(self.dim) % 1 != 0:
            raise ValueError
 
        # Generates 3D matrix mapping 1D bitmap to Hilbert's space filling curve 
        self._h_curve = np.zeros((self.dim,self.dim,self.dim), dtype=int)
        self.hilbert_curve(dim,0,0,0,1,0,0,0,1,0,0,0,1)
        self.log.info("Hilbert's curve matrix successfully initialized.")
        del self.bit_index
        self._spatial_maps = list()
        self._spatial_maps.append(self._h_curve)
        self.log.info("Hardware map: %s", h_map)
        self.log.info("Spatial map: %s", self._h_curve)
        
        # hardware map as a 1D bitarray
        self.hml = [None for _ in range(pow(len(h_map),3))]
        for i in range(self.dim):
            for j in range(self.dim):
                for k in range(self.dim):
                    self.hml[h_map[i][j][k]] = [i,j,k]
            
        # anti-diagonal identity matrix ant_d is defined as a field for reuse by remap() definition
        self.ant_d = np.eye(self.dim)
        for i in range(int(self.dim/2)):
            self.ant_d[:,[0+i,self.dim-1-i]] = self.ant_d[:,[self.dim-1-i,0+i]]
 
        self._spatial_maps.extend(self.remap())
 
    def hilbert_curve(self, dim, x, y, z, dx, dy, dz, dx2, dy2, dz2, dx3, dy3, dz3):
        """Recursively updates `SpatialCodec`'s hilbert curve matrix field a set of coordinates for
        a hilbert space filling curve with 3D resolution `dim`. Algorithm based on solution by user:
        kylefinn @ 
        https://stackoverflow.com/questions/14519267/algorithm-for-generating-a-3d-hilbert-space-filling-curve-in-python
        """
        if dim == 1:
            # Recursively fill matrix indices using temp SpatialCodec attribute bit_index
            self._h_curve[int(z)][int(x)][int(y)] = self.bit_index
            self.bit_index += 1
        else:
            dim /= 2
            if dx < 0: 
                x -= dim*dx
            if dy < 0: 
                y -= dim*dy
            if dz < 0: 
                z -= dim*dz
            if dx2 < 0: 
                x -= dim*dx2
            if dy2 < 0: 
                y -= dim*dy2
            if dz2 < 0: 
                z -= dim*dz2
            if dx3 < 0: 
                x -= dim*dx3
            if dy3 < 0: 
                y -= dim*dy3
            if dz3 < 0: 
                z -= dim*dz3
 
            self.hilbert_curve(dim, x, y, z, dx2, dy2, dz2, dx3, dy3, dz3, dx, dy, dz)
            self.hilbert_curve(dim, x+dim*dx, y+dim*dy, z+dim*dz, dx3, dy3, dz3, dx, dy, dz, dx2, 
                               dy2, dz2)
            self.hilbert_curve(dim, x+dim*dx+dim*dx2, y+dim*dy+dim*dy2, z+dim*dz+dim*dz2, dx3, dy3,
                               dz3, dx, dy, dz, dx2, dy2, dz2)
            self.hilbert_curve(dim, x+dim*dx2, y+dim*dy2, z+dim*dz2, -dx, -dy, -dz, -dx2, -dy2,
                               -dz2, dx3, dy3,dz3)
            self.hilbert_curve(dim, x+dim*dx2+dim*dx3, y+dim*dy2+dim*dy3, z+dim*dz2+dim*dz3, -dx,
                               -dy, -dz, -dx2,-dy2, -dz2, dx3, dy3, dz3)
            self.hilbert_curve(dim, x+dim*dx+dim*dx2+dim*dx3, y+dim*dy+dim*dy2+dim*dy3,
                               z+dim*dz+dim*dz2+dim*dz3,-dx3, -dy3, -dz3, dx, dy, dz, -dx2, -dy2,
                               -dz2)
            self.hilbert_curve(dim, x+dim*dx+dim*dx3, y+dim*dy+dim*dy3, z+dim*dz+dim*dz3, -dx3,
                               -dy3, -dz3, dx, dy, dz, -dx2, -dy2, -dz2)
            self.hilbert_curve(dim, x+dim*dx3, y+dim*dy3, z+dim*dz3, dx2, dy2, dz2, -dx3, -dy3,
                               -dz3, -dx, -dy, -dz)
 
    def encode(self, bits, ap_index):
        """Encodes a 1D bitmap into its corresponding `Frame` object consisting of a 3D spatial map
        of the `bitarray` index map.
 
        Args:
         - bits (`bitarray`): is the target `bitarray` for encoding.
 
        Returns:
         - frame (`Frame`): spatial map matrix constructed from from input `bitarray`
        """
        frame = Frame(self.dim)
 
        # construct spatial map matrix
        for i in range(self.dim):
            for j in range(self.dim):
                for k in range(self.dim):
                    if bits[self._spatial_maps[ap_index][i][j][k]] == 1:
                        frame.write(i,j,k)
        return frame
 
    def hardware_map(self, frame):
        """Converts spatial map to a 1D `bitarray` hardware index map. Hardware map refers to bit 
        formatting that the transmitter sends to the LED cube for broadcast. This is based on the 
        pinouts defined by TCU module.
 
        Args:
         - `frame` (`Frame`): target spatial map for conversion.
 
        Returns:
         - `bitarray` object constructed according to hardware mapping defined by the transmitter.
        """
        encoded_ba = bitarray()
        for i in range(len(self.hml)):
            encoded_ba.append(frame.read()[self.hml[i][0]][self.hml[i][1]][self.hml[i][2]])
        return encoded_ba
 
    def decode(self, frame):
        """Decodes a `Frame` spatial_map into its corresponding 1D bitmap.
 
        Args:
         - frame (`Frame`): target spatial map for decode.
 
        Returns:
         - `bits` (`bitarray`): is the decoded 1D bitmap from `Frame` object.
        """
        # bitarray defined with 0's with a length equal to the masterlist (has dim encoded by 
        # masterlist length) for 1 bit replacement
        bits = bitarray(pow(self.dim,3))
        bits.setall(False)
        spatial_map = frame.read()
 
        # adjust bitarray true values based on spatial_bitmap
        for i in range(self.dim):
            # adding 1 to each _h_curve element allows element multiplication of SM to _h_curve to 
            # yield non-zero bit indices defining positions for decoded bits
            layer_sm = np.multiply(spatial_map[i][:][:],self._spatial_maps[0][i][:][:]+1)
            for j in range(self.dim):
                for k in range(self.dim):
                    if layer_sm[j][k] != 0:
                        # subtracting 1 from each element reverts the indices to the true index 
                        # number
                        bits[layer_sm[j][k]-1] = 1
        return bits
    
    def remap(self) -> list:
        """Translates default spatial map (access point 0) to spatial maps for access points 1, 2
        and 3 located in the cardinal directions about the vertical axis of the transmitter. 
        
        Returns:
         - A list containing spatial map translations for access points 1 > 2 > 3 respectively
        """
        # generates copy of _h_curve and not a referenced pointer (_h_curve = self._h_curve creates 
        # pointer)
        _h_curve1 = self._h_curve.copy()
        _h_curve2 = self._h_curve.copy()
        _h_curve3 = self._h_curve.copy()
 
        # rotating about vertical axis requires iterative layer matrix multiplication of its
        # transpose and the anti-diagonal matrix.
        for i in range(self.dim):
            _h_curve1[i][:][:] = np.matmul(_h_curve1[i][:][:].T,self.ant_d)
        for i in range(self.dim):
            _h_curve2[i][:][:] = np.matmul(_h_curve1[i][:][:].T,self.ant_d)
        for i in range(self.dim):
            _h_curve3[i][:][:] = np.matmul(_h_curve2[i][:][:].T,self.ant_d)
        
        return [_h_curve1,_h_curve2,_h_curve3]
