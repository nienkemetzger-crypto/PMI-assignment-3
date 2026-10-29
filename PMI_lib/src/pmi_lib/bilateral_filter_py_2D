import math
import numpy as np
from pmi_lib.image import Image



def bilateral_filter_py(
        image: Image,

        sigma_s: float,  # The standard deviation of the spatial kernel (sample distance).
        sigma_r: float,  # The standard deviation of the range kernel (sample values).

) -> Image:

    array = image[...]
    if array.ndim != 2:
        raise ValueError(f"Image must be 2D, have {array.ndim} dimension(s).")


    # Initialize the result as an array of zeros with the same shape and datatype as the data.
    result = np.zeros_like(array, dtype=np.float32)

    # NumPy shape is (rows, columns) = (height, width). x is the fast column axis.
    spacing_y, spacing_x = image.spacing

    # Converting sigma_s from mm to pixels,  for each axis.
    sigma_x = sigma_s / spacing_x
    sigma_y = sigma_s / spacing_y

    # The kernel size is at least 3× the spatial SD.
    kernel_size_x = math.ceil(3 * sigma_x)
    kernel_size_y = math.ceil(3 * sigma_y)

    # Iterate over the data and apply the filter to each sample.
    for i in range(array.shape[0]):         # iterate over the first dimension of the image (e.g., rows)
        for j in range(array.shape[1]):     # iterate over the second dimension of the image (e.g., columns)
            weight_sum = 0.0  # We need to normalize the average to the sum of weights.

            # First and last neighbor samples to include in the kernel for sample i.
            start_i = max(i - kernel_size_y, 0)
            end_i = min(i + kernel_size_y, array.shape[0] - 1)
            start_j = max(j - kernel_size_x, 0)
            end_j = min(j + kernel_size_x, array.shape[1] - 1)



            # Iterate over the samples in the neighborhood.
            for ni in range(start_i, end_i + 1):
                for nj in range(start_j, end_j + 1):
                    di = i- ni  # spacial distance between samples in first dimension
                    dj = j - nj # spacial distance between samples in second dimension
                    r = array[i, j] - array[ni, nj]  # Difference in sample values

                    weight_s = np.exp(-(di**2 / (2 * sigma_y**2) + dj**2 / (2 * sigma_x**2)))
                    weight_r = np.exp(-r**2 / (2 * sigma_r**2))  # Range weight (sample values)
                    weight = weight_s * weight_r  # Net weight is the product of the spatial and range weight.

                    result[i, j] += weight * array[ni, nj]  # Add the contribution of sample (ni, nj).
                    weight_sum += weight  # Add the weight for sample (ni, nj) to the sum.


            # Normalize the average for pixel (i, j).
            result[i, j] /= weight_sum


    return Image(result, image.spacing)
