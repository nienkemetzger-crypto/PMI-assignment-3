import os
import numpy as np
import nibabel as nib
from pmi_lib.image import Image


def read_nifti(file_path: str) -> Image:
    """Reads a NIfTI file and returns an Image object containing pixel data and spacing."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Could not find file: {file_path}")

    try:
        nifti_img = nib.load(file_path)
    except Exception as e:
        raise ValueError(f"Failed to load NIfTI file {file_path}: {e}")

    pixel_data = nifti_img.get_fdata()
    # Transpose and flip array to match standard NumPy coordinate indexing
    converted_data = np.flip(np.transpose(pixel_data), axis=[0, 1])
    zooms = nifti_img.header.get_zooms()
    spacing = tuple(float(x) for x in zooms[:converted_data.ndim])

    return Image(converted_data, spacing)


def write_nifti(image: Image, file_path: str = "out.nii.gz") -> str:
    """Writes an Image object to a NIfTI file."""
    if not isinstance(image, Image):
        raise TypeError("image must be an instance of Image")

    # Extract numpy array via __array__ protocol
    data_array = np.array(image, copy=True)
    
    if data_array.dtype == bool:
        data_array = data_array.astype(np.uint8)

    # Reverse spatial orientation conversion for NIfTI output
    flipped_data = np.flip(data_array, axis=[0, 1])
    nifti_data = np.transpose(flipped_data)

    affine = np.eye(4)
    for i in range(min(len(image.spacing), 3)):
        affine[i, i] = image.spacing[i]

    nifti_img = nib.nifti1.Nifti1Image(nifti_data, affine)
    nib.nifti1.save(nifti_img, file_path)
    return file_path