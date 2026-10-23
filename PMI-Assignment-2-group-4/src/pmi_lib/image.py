import numpy as np
from typing import Any, Dict, Optional
import numpy.typing as npt

class Image:
    """A class to represent an image with pixel data and spacing information."""

    def __init__(self,
                 data: np.ndarray,
                 spacing: Optional[tuple[float | int, ...]] = None ): #: tuple[float, ...] = None):  Remove in final edit or find way to make it work for both float, int and float&int 

        #Error handling
        if not isinstance(data, np.ndarray): #error handling for data type
            raise TypeError("data must be a numpy array")
     
        self._data = data #store image data as numpy array

        if spacing is None:
            self.spacing = (1.0,) * self._data.ndim
        else:
            if not isinstance(spacing, tuple):
                raise TypeError("spacing must be a tuple")
            if not all(isinstance(x, (int, float)) for x in spacing):
                raise TypeError("spacing tuple elements must be floats or ints")
            self.spacing = tuple(float(x) for x in spacing)

        if self._data.ndim != len(self.spacing): #raise error when input dimensions do not match
            raise ValueError(f'Error: image data with shape {self._data.shape}'
                            f' not compatible with spacing tuple of size {len(self.spacing)}.')
        

    def __str__ (self) -> str:
        """Returns readable string description of the image."""
        return f"A {self._data.dtype} image with shape {self._data.shape} and a spacing of {self.spacing} mm."
    

    def __eq__(self, other) -> bool:
        """Compares two Image objects for array equality and spacing equality."""
        if not isinstance(other, Image):
            return NotImplemented
        return (np.array_equal(self._data, other._data) and
                self.spacing == other.spacing)
    

    def get_pixel_area(self) -> float:
        """Calculates pixel area in mm^2."""
        if len(self.spacing) < 2:
            raise ValueError(
                f"Insufficient dimensionality: required at least 2 dimensions, got {len(self.spacing)}."
            )
        return float(self.spacing[0] * self.spacing[1])

    def get_voxel_volume(self) -> float:
        """Calculates voxel volume in mm^3."""
        if len(self.spacing) < 3:
            raise ValueError(
                f"Insufficient dimensionality: required at least 3 dimensions, got {len(self.spacing)}."
            )
        return float(self.spacing[0] * self.spacing[1] * self.spacing[2])
    
    # --- NumPy Compatibility Dunder Methods ---

    def __len__(self) -> int:
        """Returns the length of the outer dimension of the image array."""
        return len(self._data)

    def __array__(self,
                  dtype: Optional[npt.DTypeLike] = None,
                  copy: Optional[bool] = None,) -> np.ndarray:
        """Allows NumPy functions to operate directly on Image objects
        by returning the underlying NumPy array cast to the requested dtype.
        """
        return self._data.astype(dtype, copy=copy)

    def __getitem__(self, key: Any) -> np.ndarray:
        """Enables direct indexing into the underlying image data (e.g., image[0, :, :])."""
        return self._data[key]

class DicomImage(Image): #DicomImage class that inherits from Image class
    """A class to represent a DICOM image with pixel data, spacing information, and DICOM metadata."""

    def __init__(self,
                data: np.ndarray, 
                spacing: Optional[tuple[float | int, ...]] = None,
                metadata: Optional[Dict[str, Any]] = None,) -> None:
        
        if metadata is not None and not isinstance(metadata, dict):
            raise TypeError("metadata must be a dictionary")

        super().__init__(data, spacing)
        self.metadata: Optional[Dict[str, Any]] = metadata


    def __str__(self):
        return f"A {self._data.dtype} image with shape {self._data.shape}, a spacing of {self.spacing} mm, and metadata of type {type(self.metadata)}."

    
    def __eq__(self, other: Any) -> bool: #compare two DicomImage objects
        if not isinstance(other, DicomImage):
            return NotImplemented
        return (np.array_equal(self._data, other.data) 
                and self.spacing == other.spacing 
                and self.metadata == other.metadata)

