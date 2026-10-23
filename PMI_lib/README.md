# PMI lib

A library created October 2026 for a Programming for Medical Imaging course.
It contains functions as well as an imaging class.


## The Image and DicomImage class

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
## Functions

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

### test
```python
test(path_dicom: str, path_new_nifti: str, sigma: tuple = (1.0, 1.0, 1.0))
```
A demonstration pipeline script that exercises DICOM reading, image inspections, NumPy protocols, DICOM-to-NIfTI conversion, and masked Gaussian filtering on sample datasets.

---

```
project/
├── src/
│   └── pmi_lib/
│       ├── __init__.py
│       ├── convert.py
│       ├── dicom.py
│       ├── filters.py
│       ├── image.py
│       ├── main.py
│       ├── nifti.py
│       ├── test.py
├── pyproject.toml
├── README.md
├── setup.py
├── MANIFEST.in
└── LICENSE.md
```

### How to install
Clone the repository and install the package in editable mode using `pip`:

```bash
git clone https://github.com/NielsKersten/PMI-Assignment-2-group-4.git

cd ~/PMI-Assignment-2-group-4 

python -m pip install -e .
```
uninstall by simply
```
pip uninstall pmi_lib
```

### Dependencies
- `numpy`
- `pydicom`
- `nibabel`
- `scipy`
- `click`

---

## License

`pmi-lib` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
