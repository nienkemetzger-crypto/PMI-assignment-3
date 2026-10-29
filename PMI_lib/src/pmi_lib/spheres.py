import ctypes
import numpy as np
from pathlib import Path
from pmi_lib.image import Image

def add_sphere_py(image: Image, radius: float, value: float = 1.0) -> None:
    """Adds a 3D sphere of a given radius in the center of the image with for-loops. When a pixel is inside the sphere, 
    the value is added to the current pixel value, when it's outside it does nothing

    Parameters:
        image (Image): The input image to which the sphere will be added.
        radius (float): The radius of the sphere in millimeters.
        value (float): The intensity value to assign to the voxels within the sphere.
    """
    if not isinstance(image, Image):
        raise TypeError("image must be an instance of Image")

    # Access the underlying data array 
    data = image._data
    spacing = list(image.spacing)
    
    # Create a view of the data with 3 dimensions if the original image is 1D or 2D
    data_view = data
    while data_view.ndim < 3:
        data_view = data_view[None] # Adds 1 dimension at the beginning
        spacing.insert(0, 1.0)      # Prepend default spacing for the padded dimension

    nz, ny, nx = data_view.shape
    sz, sy, sx = spacing

    # Calculate the continuous center index of the image
    cz = (nz - 1) / 2.0
    cy = (ny - 1) / 2.0
    cx = (nx - 1) / 2.0

    # Cache the squared radius to avoid computing the square root inside the loop
    radius_sq = radius ** 2

    # Iterate over all pixels using plain for-loops
    for z in range(nz):
        for y in range(ny):
            for x in range(nx):
                # Calculate physical distance squared from the center in mm
                dz = (z - cz) * sz
                dy = (y - cy) * sy
                dx = (x - cx) * sx
                
                # If the pixel is inside the sphere, add the value
                if (dx*dx + dy*dy + dz*dz) <= radius_sq:
                    data_view[z, y, x] += value

def add_sphere_np(image: Image, radius: float, value: float = 1.0) -> None:
    """Adds a 3D sphere of a given radius in the center of the image using NumPy vectorized operations. 
    When a pixel is inside the sphere, the value is added to the current pixel value, when it's outside it does nothing.

    Parameters:
        image (Image): The input image to which the sphere will be added.
        radius (float): The radius of the sphere in millimeters.
        value (float): The intensity value to assign to the voxels within the sphere.
    """
    if not isinstance(image, Image):
        raise TypeError("image must be an instance of Image")

    # Access the underlying data array
    data = image._data
    spacing = list(image.spacing)

    # Create a view of the data with 3 dimensions if the original image is 1D or 2D
    data_view = data
    while data_view.ndim < 3:
        data_view = data_view[None]  # Adds 1 dimension at the beginning
        spacing.insert(0, 1.0)       # Prepend default spacing for the padded dimension

    nz, ny, nx = data_view.shape
    sz, sy, sx = spacing

    # Calculate the continuous center index of the image
    cz = (nz - 1) / 2.0
    cy = (ny - 1) / 2.0
    cx = (nx - 1) / 2.0

    # Create coordinate grids for each dimension
    z_grid, y_grid, x_grid = np.indices((nz, ny, nx))

    # Calculate physical distances from the center in mm
    dz = (z_grid - cz) * sz
    dy = (y_grid - cy) * sy
    dx = (x_grid - cx) * sx

    # Compute squared distances from the center
    distance_sq = dx**2 + dy**2 + dz**2

    # Add value to pixels inside the sphere using boolean indexing
    data_view[distance_sq <= radius**2] += value

# Load the compiled library
_lib = np.ctypeslib.load_library("pmi", Path(__file__).parent)

# Define the C interface signatures
_lib.add_sphere.argtypes = [
    np.ctypeslib.ndpointer(dtype=np.float64, flags='C_CONTIGUOUS'),
    ctypes.c_size_t, ctypes.c_size_t, ctypes.c_size_t,
    ctypes.c_double, ctypes.c_double, ctypes.c_double,
    ctypes.c_double, ctypes.c_double
]
_lib.add_sphere.restype = ctypes.c_int

def add_sphere(image: Image, radius: float, value: float = 1.0) -> None:
    """Adds a 3D sphere of a given radius in the center of the image using a compiled C function. 
    When a pixel is inside the sphere, the value is added to the current pixel value, when it's outside it does nothing.

    Parameters:
        image (Image): The input image to which the sphere will be added.
        radius (float): The radius of the sphere in millimeters.
        value (float): The intensity value to assign to the voxels within the sphere.
    """
    if not isinstance(image, Image):
        raise TypeError("image must be an instance of Image")

    # Ensure data is C-contiguous and float64 for the C function
    data = np.ascontiguousarray(image._data, dtype=np.float64)
    spacing = list(image.spacing)

    # Pad to 3 dimensions
    while data.ndim < 3:
        data = data[None]
        spacing.insert(0, 1.0)

    nz, ny, nx = data.shape
    sz, sy, sx = spacing

    # Call the C function
    status = _lib.add_sphere(data, nx, ny, nz, sx, sy, sz, radius, value)
    
    if status != 0:
        raise ValueError("C function failed with a non-zero status.")

    # Remove the padded dimensions to match the original image shape
    data = np.squeeze(data)

    # Reassign the modified data array back to the original image slice. 
    image[:] = data.astype(image._data.dtype)