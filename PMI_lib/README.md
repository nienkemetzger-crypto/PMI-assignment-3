# PMI lib

A library created October 2026 for a Programming for Medical Imaging course.
It contains functions as well as an imaging class.

## Requirements

- Python 3.12 or later
- GCC, to compile the native C code during installation

Install GCC before installing the package if it is not already available. On Windows, the `setup.py` build script reports installation guidance if it cannot find GCC.

### installation
Clone the repository and install the package in editable mode using `pip`:

```bash
git clone https://github.com/NielsKersten/PMI-Assignment-2-group-4.git

cd ~/PMI-Assignment-3 

python -m pip install -e .
```
uninstall by simply
```
pip uninstall pmi_lib
```

## The Image classes

### Image 
```python
Image(data: np.ndarray, spacing: Optional[tuple[float | int, ...]] = None)
```

Image supports N-dimensional images. 

Stores the spacing as a tuple of floats(millimeters) in the class attribute `.spacing`, and the image data as a NumPy array in the hidden class attribute `._data`.

- **Attributes:**
  - `._data` (`np.ndarray`): The pixel/voxel array.
  - `.spacing` (`tuple[float, ...]`): Tuple of spatial spacing per dimension in mm. Defaults to `1.0` for each dimension if not specified.
- **Methods & Protocols:**
  - `get_pixel_area()`: Calculates the 2D pixel area in $\text{mm}^2$. Requires at least 2 dimensions.
  - `get_voxel_volume()`: Calculates the 3D voxel volume in $\text{mm}^3$. Requires at least 3 dimensions.
  - `__len__()`: Returns the length of the outer dimension of the image array.
  - `__array__(dtype=None, copy=None)`: Allows NumPy functions to operate directly on `Image` objects.
  - `__getitem__(key)`: Enables direct array indexing/slicing.
  - `__str__()`: Returns a string representation of array data type, shape, and spacing.
  - `__eq__(other)`: Checks equality for both the underlying array data and spacing values.

---

### DicomImage
```python
DicomImage(
    data: np.ndarray, 
    spacing: Optional[tuple[float | int, ...]] = None, 
    metadata: Optional[Dict[str, Any]] = None)
```


Inherits class attributes from `Image` with an additional class attribute `metadata`.

- **Attributes:**
  - Inherits `._data` and `.spacing` from `Image`.
  - `.metadata` (`Optional[Dict[str, Any]]`): Metadata dictionary containing DICOM header tags.
- **Methods:**
  - `__str__()`: Includes string description of data type, shape, spacing, and metadata object type.
  - `__eq__(other)`: Checks equality across array data, spacing, and metadata dictionary.

---
## Reading and writing medical images

### read_dicom
```python
read_dicom(file_path: str) -> DicomImage
```
Reads a single DICOM slice or a directory of DICOM slices and returns a `DicomImage` object.
- Automatically computes voxel spacing based on slice tags.
- Rescales pixel values to CT Hounsfield Units ($\text{PixelValue} \times \text{RescaleSlope} + \text{RescaleIntercept}$).
- Orders directory slices by their physical $z$-coordinate (`ImagePositionPatient`).
- Parses DICOM header attributes into `.metadata`.

---

### read_nifti
```python
read_nifti(file_path: str) -> Image
```
Reads a `.nii` or `.nii.gz` file using `nibabel` and returns an `Image` object.
- Transposes and flips image orientation to align with NumPy indexing conventions.
- Extracts spatial voxel dimensions from the header into `.spacing`.

---

### write_nifti
```python
write_nifti(image: Image, file_path: str = "out.nii.gz") -> str
```
Exports an `Image` or `DicomImage` instance to NIfTI format.
- Reverses spatial coordinate transforms for correct NIfTI storage.
- Automatically constructs a 4x4 affine matrix scaled by `image.spacing`.
- Converts boolean arrays to `uint8` if necessary.

---

### dicom_to_nifti
```python
dicom_to_nifti(file_path_dicom: str, file_path_nifti: str) -> None
```
Reads a DICOM file or directory and saves it as a NIfTI file.

---
## Filters


### masked_gaussian_filter
```python
masked_gaussian_filter(
    image: Image, 
    mask: Image | np.ndarray, 
    sigma: tuple[float, ...]
) -> Image
```
Applies a normalized Gaussian filter to an `Image` object.
- `sigma` is provided in physical millimeter units ($\text{mm}$) and dynamically converted to voxel units ($\sigma_{\text{pixels}} = \frac{\sigma_{\text{mm}}}{\text{spacing}}$).
- Performs normalized convolution to eliminate border artifacts near mask edges.

---

### bilateral_filter
```python
bilateral_filter(image: Image, sigma_s: float, sigma_r: float) -> Image
```
Applies a 2D bilateral filter using compiled C code. `sigma_s` is the spatial standard deviation in millimeters; `sigma_r` is the standard deviation for intensity values.

---

### Slice processing
```python
apply_to_slices(image: Image, f: Callable, *args, **kwargs) -> Image
apply_to_slices_parallel(image: Image, f: Callable, *args, **kwargs) -> Image
```
Applies a 2D function to each slice of a 3D `image` and returns the processed slices as a 3D Image. The parallel version uses joblib threads and chooses up to the number of CPU cores minus one, with at least one worker.

---

### Spherical measurements
```python
SphericalMeasurement(radius: float, functions: dict[str, Callable])
```
Creates a callable measurement object. The radius is in millimeters. Each function should accept a one-dimensional NumPy array of voxel values and return a statistic.

```python
import numpy as np
from pmi_lib import SphericalMeasurement, read_nifti

image = read_nifti("ct_jaw.nii.gz")
measurement = SphericalMeasurement(
    20,
    {"mean": np.mean, "stddev": np.std, "max": np.max},
)
result = measurement(image, 381, 300, 60)

print(result["mean"])
cropped_image = result["cropped_image"]
```
The result includes each requested statistic and a cropped `Image` with the measured sphere highlighted.

---
## Tests and examples

The scripts below are examples and comparison checks. They print results; they are not configured as an automated test suite.

### test.py
```python
test(path_dicom: str, path_new_nifti: str, sigma: tuple = (1.0, 1.0, 1.0))
```
This script demonstrates DICOM and NIfTI reading, image properties, NumPy compatibility, masked Gaussian filtering, and sequential and parallel slice processing. It also displays images with `pmi_viewer`.

Run it from a directory that contains the sample DICOM file `ct_thorax_slice.dcm` and the `ct_jaw` directory, or their parent directory:

### test_filters&spheres.py
```python
test(path_dicom: str, path_new_nifti: str, sigma: tuple = (1.0, 1.0, 1.0))
```
This script compares the Python and C bilateral filters, compares the Python, NumPy, and C sphere implementations, and compares sequential and parallel slice processing with bilateral and median filters.

---

```
project/
├── src/
│   └── pmi_lib/
│       ├── __init__.py
│       ├── bilateral_filter_2D.c
│       ├── bilateral_filter_py.py
│       ├── bilateral_filter.py
│       ├── convert.py
│       ├── dicom.py
│       ├── filters.py
│       ├── image.py
│       ├── main.py
│       ├── multithreading.py
│       ├── nifti.py
│       ├── spheres.c
│       ├── spheres.py
│       ├── spherical_measurement.py
│       ├── test_filters&spheres.py
│       ├── test.py
├── pyproject.toml
├── README.md
├── setup.py
├── MANIFEST.in
└── LICENSE.md
```



### Dependencies
- `nibabel`
- `numpy`
- `pydicom`
- `pmi_viewer`
- `scipy`
- `click`
- `gdcm`
- `pylibjpeg`
- `pylibjpeg-libjpeg`
- `joblib`


The C code is compiled during installation. GCC is a system compiler and must be installed separately.

---

## License

`pmi-lib` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
