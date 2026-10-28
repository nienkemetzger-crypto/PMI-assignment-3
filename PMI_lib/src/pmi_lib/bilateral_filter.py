from ctypes import c_double, c_int, c_size_t
from pathlib import Path

import numpy as np
from numpy.ctypeslib import ndpointer

from .image import Image

# Load the compiled C library (pmi.dll / libpmi.so / libpmi.dylib) that sits next to this file.
_lib = np.ctypeslib.load_library("pmi", Path(__file__).parent)

# Declare the C signature so ctypes passes the arguments correctly:
# int bilateral_filter(double *data, size_t width, size_t height,
#                      double sigma_x, double sigma_y, double sigma_r, double *result)
_lib.bilateral_filter.argtypes = [
    ndpointer(np.float64, flags="C_CONTIGUOUS"),  # data
    c_size_t,  # width  (pixels in x)
    c_size_t,  # height (pixel in y)
    c_double,  # sigma_x (pixels)
    c_double,  # sigma_y (pixels)
    c_double,  # sigma_r (pixel values)
    ndpointer(np.float64, flags="C_CONTIGUOUS,WRITEABLE"),  # result
]
_lib.bilateral_filter.restype = c_int


def bilateral_filter(image: Image, sigma_s: float, sigma_r: float) -> Image:
    """Applies a bilateral filter (2D) using the compiled c library.
    Args:
        image: A 2D Image.
        sigma_s: Standard deviation of the spatial kernel, in millimeters.
        sigma_r: Standard deviation of the range kernel, in pixel values.
    Returns a new Image with the filtered data and the same spacing.
    Raises a ValueError if the image is not 2D, or if the C function reports an error.
    """
    array = image[...]
    if array.ndim != 2:
        raise ValueError(f"Image must be 2D, have {array.ndim} dimension(s).")

    # The c code expects contiguous float64 memory.
    data = np.ascontiguousarray(array, dtype=np.float64)
    result = np.empty_like(data)

    # NumPy shape is (rows, columns) = (height, width). x is the fast column axis.
    height, width = data.shape
    spacing_y, spacing_x = image.spacing

    # Converting sigma_s from mm to pixels,  for each axis.
    sigma_x = sigma_s / spacing_x
    sigma_y = sigma_s / spacing_y

    status = _lib.bilateral_filter(data, width, height, sigma_x, sigma_y, sigma_r, result)
    if status != 0:
        raise ValueError(f"bilateral_filter failed with status code {status} (invalid arguments).")

    return Image(result, image.spacing)