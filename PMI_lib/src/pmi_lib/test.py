import os 
import numpy as np
from typing import Any, Dict, Optional
from pmi_viewer import view 
from pmi_lib import * 


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


    ### Test out image class
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

    # 2. NumPy compatibility tests
    print("\n=== NumPy Compatibility ===")
    print(f"Image length (outer dimension): {len(im1)}")
    print(f"Shape via NumPy: {np.shape(im1)}")
    print(f"Dimensions via NumPy: {np.ndim(im1)}")
    print(f"Slicing result shape [0]: {im1[0].shape}")

    # 3. DicomImage Initialization
    if metadata is None:
        metadata = {"PatientName": "Jan Jansen", "PatientID": "123"}

    im_dicom = DicomImage(data, spacing, metadata)
    print("\n=== DicomImage Info ===")
    # print(im_dicom)
    print(f"DICOM Metadata: Patient name: {im_dicom.metadata["PatientName"]}, Patient age: {im_dicom.metadata["PatientAge"]}")

    # # Dicom to nifti + read_nifti
    print("\n===dicom_to_nifti===")
    dicom_to_nifti(path_dicom, path_new_nifti)
    image_new_nifti = read_nifti(path_new_nifti)
    print("Nift image, created by dicom to nifti of last dicom image, read by read_nifti  ")
    view(image_new_nifti._data, spacing = image_new_nifti.spacing)

    # #gaussian filter
    print("\n===masked_gaussian_filter==")
    np_array_mask = image_new_nifti._data > 0
    mask = Image(np_array_mask,spacing = image_new_nifti.spacing)
    gauss = masked_gaussian_filter(image_new_nifti, mask, sigma)
    print("Gaussian filter applied over data of Nifti image")
    view(gauss, spacing=image_new_nifti.spacing)



file_path = pathfinder("ct_thorax_slice.dcm")
dir_path = pathfinder("ct_jaw")
new_nifti_path = dir_path.replace("ct_jaw", "new_nifti.nii.gz")


test(file_path,new_nifti_path, sigma = (1.0,1.0))
test(dir_path,new_nifti_path, sigma = (1.0,1.0,1.0))

