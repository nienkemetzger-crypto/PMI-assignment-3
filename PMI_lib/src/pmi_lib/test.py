import os 
import numpy as np
from typing import Any, Dict, Optional
from pmi_viewer import view 
from pmi_lib import *
import time


## To make the code cross compatible for our systems
def pathfinder(filename):
    for root, dirs, files in os.walk(os.getcwd()):
        if filename in files:
            return(os.path.join(root, filename))
        if filename in dirs:
            return(os.path.join(root, filename))



def test(path_dicom: str, 
         path_new_nifti:str, 
         sigma: tuple = (1.0,1.0,1.0)): #tuple[float, ...] = (1.0,1.0,1.0)):
    """test the image class and all functions,   
    input: dicom filepath (str), filepath for new nifti file (str), std deviation for masked gaussian in mm (tuple) = (1.0, 1.0,1.0)"""

    ## read_dicom
    print("===read_dicom===")
    image_dicom = read_dicom(path_dicom)
    print("Dicom image read by read_dicom, viewed with pmi_viewer \n")
    view(image_dicom._data, spacing = image_dicom.spacing)


    # Test out image class
    data = image_dicom._data
    spacing = image_dicom.spacing
    metadata = image_dicom.metadata
    if data is None:
        data = np.ones((10, 10, 10), dtype=np.float32)

    im1 = Image(data, spacing)
    print("=== Image Info ===")
    print(im1)

    # Safely attempt area calculation
    try:
        print(f"Pixel Area: {im1.get_pixel_area()} mm^2")
    except ValueError as e:
        print(f"Pixel Area: Couldn't calculate ({e})")

    # Safely attempt volume calculation
    try:
        print(f"Voxel Volume: {im1.get_voxel_volume()} mm^3")
    except ValueError as e:
        print(f"Voxel Volume: Couldn't calculate ({e})")

    # NumPy compatibility tests
    print("\n=== NumPy Compatibility ===")
    print(f"Image length (outer dimension): {len(im1)}")
    print(f"Shape via NumPy: {np.shape(im1)}")
    print(f"Dimensions via NumPy: {np.ndim(im1)}")
    print(f"Slicing result shape [0]: {im1[0].shape}")

    # DicomImage Initialization
    if metadata is None:
        metadata = {"PatientName": "Jan Jansen", "PatientID": "123"}

    im_dicom = DicomImage(data, spacing, metadata)
    print("\n=== DicomImage Info ===")
    # print(im_dicom)
    print(f"DICOM Metadata: Patient name: {im_dicom.metadata["PatientName"]}, Patient age: {im_dicom.metadata["PatientAge"]}")

    # Dicom to nifti + read_nifti
    print("\n===dicom_to_nifti===")
    dicom_to_nifti(path_dicom, path_new_nifti)
    image_new_nifti = read_nifti(path_new_nifti)
    print("Nift image, created by dicom to nifti of last dicom image, read by read_nifti  ")
    view(image_new_nifti._data, spacing = image_new_nifti.spacing)

    # gaussian filter
    print("\n===masked_gaussian_filter==")
    np_array_mask = image_new_nifti._data > 0
    mask = Image(np_array_mask,spacing = image_new_nifti.spacing)
    gauss = masked_gaussian_filter(image_new_nifti, mask, sigma)
    print("Gaussian filter applied over data of Nifti image")
    view(gauss, spacing=image_new_nifti.spacing)

    # apply_to_slices
    print("\n===apply_to_slices===")
    if image_new_nifti._data.ndim == 3:
        # Simple 2D function: add 100 to every pixel of a slice
        def add_offset(slice_image, offset):
            return Image(slice_image._data + offset, spacing=slice_image.spacing)

        result_seq = apply_to_slices(image_new_nifti, add_offset, 100)

        print(f"Input shape: {np.shape(image_new_nifti)}, output shape: {np.shape(result_seq)}")
        print(f"Spacing kept: {result_seq.spacing == image_new_nifti.spacing}")
        print(f"Values correct: {np.allclose(result_seq._data, image_new_nifti._data + 100)}")
        view(result_seq._data, spacing=result_seq.spacing)
        result_par = apply_to_slices_parallel(image_new_nifti, add_offset, 100)
        print(f"Parallel equals sequential: {np.array_equal(result_seq._data, result_par._data)}")

        # Timing comparison with a heavier 2D function
        from scipy.ndimage import gaussian_filter

        def blur(slice_image, sigma):
            return Image(gaussian_filter(slice_image._data, sigma), spacing=slice_image.spacing)

        start = time.perf_counter()
        apply_to_slices(image_new_nifti, blur, 5)
        t_seq = time.perf_counter() - start

        start = time.perf_counter()
        apply_to_slices_parallel(image_new_nifti, blur, 5)
        t_par = time.perf_counter() - start

        print(f"Sequential: {t_seq:.2f}s, parallel: {t_par:.2f}s")
    else:
        print("Skipped: apply_to_slices needs a 3D image")
    
    # SphericalMeasurement
    print("\n===SphericalMeasurement===")
    if image_new_nifti._data.ndim == 3:
        measurement = SphericalMeasurement(
            20, {"mean": np.mean, "stddev": np.std, "max": np.max}
        )
        result = measurement(image_new_nifti, 381, 300, 60)
        print(
            f"Mean: {result['mean']:.2f}, StdDev: {result['stddev']:.2f}, Max: {result['max']:.2f}"
        )
        cropped = result["cropped_image"]
        view(cropped._data, spacing=cropped.spacing)


file_path = pathfinder("ct_thorax_slice.dcm")
dir_path = pathfinder("ct_jaw")
new_nifti_path = dir_path.replace("ct_jaw", "new_nifti.nii.gz")


test(file_path,new_nifti_path, sigma = (1.0,1.0))
test(dir_path,new_nifti_path, sigma = (1.0,1.0,1.0))

