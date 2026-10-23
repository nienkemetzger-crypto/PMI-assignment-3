import numpy as np
from scipy.ndimage import gaussian_filter
from pmi_lib.image import Image


def masked_gaussian_filter(
    image: Image,
    mask: Image | np.ndarray,
    sigma: tuple[float, ...],
) -> Image:
    """Applies a masked Gaussian filter to an Image.
    
    `sigma` is given in millimeters and converted to pixels using image spacing.
    """
    if not isinstance(image, Image):
        raise TypeError("image must be an instance of Image")

    image_array = np.array(image, dtype=np.float32)

    if isinstance(mask, Image):
        mask_array = np.array(mask, dtype=np.float32)
    elif isinstance(mask, np.ndarray):
        mask_array = mask.astype(np.float32)
    else:
        raise TypeError("mask must be an Image or numpy array")

    if len(sigma) != image_array.ndim:
        raise ValueError("sigma length must match the dimensionality of the image")

    # Convert sigma from physical units (mm) to voxel/pixel units using spacing
    sigma_pixels = tuple(s / sp for s, sp in zip(sigma, image.spacing))

    gauss_masked_image = gaussian_filter(image_array * mask_array, sigma=sigma_pixels)
    gauss_mask = gaussian_filter(mask_array, sigma=sigma_pixels)

    with np.errstate(divide="ignore", invalid="ignore"):
        masked_gauss_filtered_image = mask_array * (gauss_masked_image / gauss_mask)

    result_array = np.nan_to_num(masked_gauss_filtered_image)
    return Image(result_array, image.spacing)