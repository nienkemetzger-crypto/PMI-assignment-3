from pmi_lib.image import Image
import numpy as np
from typing import Any, Callable

class SphericalMeasurement:
    """
    A class for performing statistical measurements on a spherical volume of a 3D image.
    """


    def __init__(self, radius: float, functions: dict[str, Callable]):
        """
        Initializes the SphericalMeasurement class with a specified radius and a dictionary of functions.

        Parameters:
        - radius (float): The radius of the sphere for measurement in mm.
        - functions (dict[str, Callable]): A dictionary where keys are function names and values are callable functions.
        """
        #Error handling
        if not isinstance(radius, (int, float)): #error handling for data type
            raise TypeError("radius must be a number in mm")
        if radius <= 0:
            raise ValueError("radius must be positive")
        
        if not isinstance(functions, dict): #error handling for data type
            raise TypeError("functions must be a dictionary of strings mapped to callable functions")
        for name, fn in functions.items():
            if not isinstance(name, str) or not callable(fn):
                raise TypeError("functions must map strings to callable functions")

        
        self.radius = radius # in mm
        self.functions = functions # dictionary of strings (mnemonic names) mapped to (statistical) functions that can be applied to 1-dimensional NumPy array


  
    def __call__(self, image: Image, x: int, y: int, z: int) -> dict[str, Any]:
        """
        Applies the specified functions to the voxels within a sphere of the given radius centered at (x, y, z) in the image.
        Parameters:
        - image (Image): The 3D image on which to perform the measurement.
        - x (int): The x-coordinate of the sphere's center in voxel indices.
        - y (int): The y-coordinate of the sphere's center in voxel indices.
        - z (int): The z-coordinate of the sphere's center in voxel indices.
        Returns:
        - dict[str, Any]: A dictionary containing the measurement results and a cropped Image object with the sphere overlaid on the image.
        """
        array = image[...]

        if array.ndim != 3:  # Ensure the image is 3D
            raise ValueError("image must be a 3D array")
        if not all(isinstance(coord, int) for coord in (x, y, z)):
            raise TypeError("x, y, and z must be integers")      


        nz, ny, nx = array.shape

        # image.spacing is in (x, y, z) order, but the array is (z, y, x).
        # Reverse it so each entry lines up with its array axis.
        spacing_z, spacing_y, spacing_x = image.spacing[2], image.spacing[1], image.spacing[0]

        radius_z = self.radius / spacing_z
        radius_y = self.radius / spacing_y
        radius_x = self.radius / spacing_x

        # Whole-voxel extent of the sphere along each array axis
        rz = int(np.floor(radius_z))
        ry = int(np.floor(radius_y))
        rx = int(np.floor(radius_x))

        if not (0 <= z < nz and 0 <= y < ny and 0 <= x < nx):
            raise ValueError("x, y, and z must be within the bounds of the image dimensions")
        if (z - rz < 0 or z + rz >= nz or
                y - ry < 0 or y + ry >= ny or
                x - rx < 0 or x + rx >= nx):
            raise ValueError("Sphere extends beyond image boundaries. Check the x, y, z coordinates and radius value.")

        # Boolean mask over the full image, in array order (z, y, x)
        zz, yy, xx = np.ogrid[:nz, :ny, :nx]
        sphere_mask = (((zz - z) / radius_z) ** 2 +
                    ((yy - y) / radius_y) ** 2 +
                    ((xx - x) / radius_x) ** 2) <= 1

        # Statistics on the voxels inside the sphere
        measurements = {}
        for name, func in self.functions.items():
            measurements[name] = func(array[sphere_mask])

        # Cropped box around the sphere, in array order
        crop_slices = (slice(z - rz, z + rz + 1),
                    slice(y - ry, y + ry + 1),
                    slice(x - rx, x + rx + 1))
        crop = array[crop_slices].astype(float)
        crop_mask = sphere_mask[crop_slices]

        # create bright overlay of the sphere on the cropped image, for visualization
        hi = crop.max()
        overlay = crop.copy()
        overlay[crop_mask] = 0.8 * crop[crop_mask]  +  hi 

        measurements["cropped_image"] = Image(overlay, image.spacing)
      
        return measurements
