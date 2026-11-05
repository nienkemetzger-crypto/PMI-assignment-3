from typing import Callable
import numpy as np
from pmi_lib.image import Image
from joblib import Parallel, delayed, cpu_count

def apply_to_slices(image_3d: Image, slice_func: Callable, *args, **kwargs) -> Image:
    """A 2D function is applied to each slice of a 3D image:
    Each slice is wrapped in an Image (with the 2D spacing) and passed to
    ``slice_func``, which takes a 2D Image including any additional arguments and returns
    a 2D result. The processed slices are stacked back into a 3D image with
    the same spacing as the input.
    """
    # First, the 2D slice needs one spacing value less than the 3D volume
    slice_spacing = image_3d.spacing[:-1]

    # Next, each slice is converted to an Image so the function also gets the spacing
    input_slices = [Image(s, spacing=slice_spacing) for s in image_3d]

    # Each slice is processed independently
    processed_slices = [slice_func(s, *args, **kwargs) for s in input_slices]

    # the results are stacked into a 3D array and the original spacing is restored
    return Image(np.array(processed_slices), spacing=image_3d.spacing)



def apply_to_slices_parallel(image_3d: Image, slice_func: Callable, *args, **kwargs) -> Image:
    """Like ``apply_to_slices``, but processes the slices in parallel threads.
    Uses joblib with the number of CPU cores minus one (at least one) workers.
    """
    # Use all cores but one (never less than one)
    n_jobs = max(1, cpu_count() - 1)

    # Prepare the slices exactly as in the sequential version
    slice_spacing = image_3d.spacing[:-1]
    input_slices = [Image(s, spacing=slice_spacing) for s in image_3d]

    # Process the slices in parallel threads; results keep the input order
    processed_slices = Parallel(n_jobs=n_jobs, prefer="threads")(
        delayed(slice_func)(s, *args, **kwargs) for s in input_slices
    )

    # Stack results into a 3D array and restore the original spacing
    return Image(np.array(processed_slices), spacing=image_3d.spacing)