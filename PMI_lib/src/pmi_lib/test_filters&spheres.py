import numpy as np
from pmi_lib.image import Image
from pmi_lib.spheres import add_sphere, add_sphere_py, add_sphere_np
from pmi_lib.bilateral_filter import bilateral_filter
from pmi_lib.bilateral_filter_py import bilateral_filter_py
from pmi_lib.multithreading import apply_to_slices, apply_to_slices_parallel
import time
from scipy.ndimage import median_filter

def test_parallel():
    """Compare sequential and parallel slice filtering, timings, and results."""
    noise = np.random.randn(50, 128, 128)
    image = Image(noise, spacing=(1.0, 1.0, 2.0))
    add_sphere(image, radius=50, value=10)

    def compare(label, function, **kwargs):
        start = time.perf_counter()
        sequential = apply_to_slices(image, function, **kwargs)
        sequential_time = time.perf_counter() - start

        start = time.perf_counter()
        parallel = apply_to_slices_parallel(image, function, **kwargs)
        parallel_time = time.perf_counter() - start

        difference = np.mean(
            (np.asarray(sequential) - np.asarray(parallel)) ** 2
        )

        print(f"{label}:")
        print(f"  sequential: {sequential_time:.3f} s")
        print(f"  parallel:   {parallel_time:.3f} s")
        print(f"  mean squared difference: {difference:.12g}")

    compare(
        "Bilateral filter",
        bilateral_filter,
        sigma_s=5.0,
        sigma_r=2.0,
    )

    # scipy's filter takes arrays; convert each Image slice explicitly.
    def median_filter_2d(slice_image, size):
        return median_filter(np.asarray(slice_image), size=size)

    compare("Median filter", median_filter_2d, size=13)

def test_filters():
    """
    Tests the 2D bilateral filter implementations (Python vs C) 
    and prints the mean squared difference.
    """
    noise = np.random.randn(50, 100) 
    image = Image(noise, spacing=(1.0, 2.0)) 
    add_sphere(image, radius=30, value=10) 
    
    result_py = bilateral_filter_py(image, sigma_s=5.0, sigma_r=2.0)
    result_c = bilateral_filter(image, sigma_s=5.0, sigma_r=2.0)
    
    # Measure and print the mean squared difference
    msd = np.mean((np.array(result_py) - np.array(result_c)) ** 2)
    print(f"Mean squared difference between Python and C filters: {msd}")
    print(f"Is it close to zero? {'Yes' if msd < 1e-10 else 'No'}")


def test_spheres():
    """
    Tests the three 3D sphere implementations by creating identical volumes,
    adding overlapping spheres, and printing the mean squared differences.
    """
    # Create 3 identical 3D volumes with anisotropic spacing
    shape = (30, 40, 50)
    spacing = (1.5, 1.0, 2.0)
    
    img_py = Image(np.zeros(shape), spacing=spacing)
    img_np = Image(np.zeros(shape), spacing=spacing)
    img_c = Image(np.zeros(shape), spacing=spacing)
    
    # Add a few overlapping spheres
    spheres = [
        {"radius": 10.0, "value": 5.0},
        {"radius": 15.0, "value": 3.0}
    ]
    
    # Use a different add_spheres implementation for each volume
    for params in spheres:
        add_sphere_py(img_py, **params)
        add_sphere_np(img_np, **params)
        add_sphere(img_c, **params)
        
    # Measure and print the mean squared difference between all three images
    msd_py_np = np.mean((np.array(img_py) - np.array(img_np)) ** 2)
    msd_py_c = np.mean((np.array(img_py) - np.array(img_c)) ** 2)
    msd_np_c = np.mean((np.array(img_np) - np.array(img_c)) ** 2)
    
    print(f"MSD between plain loops (py) and vectorized (np): {msd_py_np}")
    print(f"MSD between plain loops (py) and C extension (c): {msd_py_c}")
    print(f"MSD between vectorized (np) and C extension (c): {msd_np_c}")
    
    # Is it zero?
    is_zero = (msd_py_np == 0.0) and (msd_py_c == 0.0) and (msd_np_c == 0.0)
    print(f"Are all mean squared differences exactly zero? {'Yes' if is_zero else 'No'}")

if __name__ == "__main__":
    print("--- Running test_spheres ---")
    test_spheres()
    
    print("\n--- Running test_filters ---")
    test_filters() 

    print("\n--- Running test_parallel ---")
    test_parallel()