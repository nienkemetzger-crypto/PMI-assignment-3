import os
import numpy as np
from pydicom import dcmread
from pmi_lib.image import DicomImage


def _get_z_position(dicom_dataset):
    """Returns the z-coordinate from ImagePositionPatient tag."""
    return dicom_dataset.ImagePositionPatient[2]


def _get_spacing(dicom_slices: list) -> tuple[float, ...]:
    """Calculates pixel spacing in mm for 2D or 3D DICOM datasets."""
    n = len(dicom_slices)
    dx, dy = dicom_slices[0].PixelSpacing

    if n > 1:
        z_first = np.array(dicom_slices[0].ImagePositionPatient)
        z_last = np.array(dicom_slices[-1].ImagePositionPatient)
        dz = np.linalg.norm(z_last - z_first) / (n - 1)
        return (float(dx), float(dy), float(dz))
    
    return (float(dx), float(dy))


def read_dicom(file_path: str) -> DicomImage:
    """Reads a DICOM file or directory of DICOM slices and returns a DicomImage object."""
    if os.path.isfile(file_path):
        ds = dcmread(file_path)
        pixel_values = ds.pixel_array
        spacing = _get_spacing([ds])

        slope = getattr(ds, "RescaleSlope", 1.0)
        intercept = getattr(ds, "RescaleIntercept", 0.0)
        ct_values = pixel_values * slope + intercept

        # Creates a dictionary of DICOM attributes where item.keyword is the attribute string name
        # and item.value is its corresponding tag value, while excluding large raw PixelData bytes.
        metadata = {
            item.keyword: item.value
            for item in ds
            if item.keyword and item.keyword != "PixelData"
        }

    elif os.path.isdir(file_path):
        dicom_files = [
            os.path.join(file_path, f)
            for f in os.listdir(file_path)
            if os.path.isfile(os.path.join(file_path, f))
        ]
        if not dicom_files:
            raise FileNotFoundError(f"No files found in directory: {file_path}")

        dicom_datasets = [dcmread(f) for f in dicom_files]
        dicom_datasets = sorted(dicom_datasets, key=_get_z_position)

        series_uids = [ds.SeriesInstanceUID for ds in dicom_datasets]
        if not all(uid == series_uids[0] for uid in series_uids):
            raise ValueError(f"Directory {file_path} contains multiple Series Instance UIDs.")

        pixel_slices = []
        for ds in dicom_datasets:
            slope = getattr(ds, "RescaleSlope", 1.0)
            intercept = getattr(ds, "RescaleIntercept", 0.0)
            pixel_slices.append(ds.pixel_array * slope + intercept)

        ct_values = np.array(pixel_slices)
        spacing = _get_spacing(dicom_datasets)

        # Extract metadata from the first slice in the sorted series
        metadata = {
            item.keyword: item.value
            for item in dicom_datasets[0]
            if item.keyword and item.keyword != "PixelData"
        }

    else:
        raise FileNotFoundError(f"Could not find file or directory: {file_path}")

    return DicomImage(ct_values, spacing, metadata)