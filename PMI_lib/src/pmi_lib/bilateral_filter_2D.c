#include <stddef.h>  // Provides size_t
#include <math.h>    // Provides exp() and ceil function
#include <stdlib.h>  // Provides malloc and free

//  Applies a 2-dimensional bilateral filter.
//  Returns 0 on success, -1 on invalid arguments.
int bilateral_filter(
    double *data,      // Pointer to a 1-dimensional array.
    size_t width,      // A 2D image has a width and height.
    size_t height,     // A 2D image has a width and height.
    double sigma_x,    // The spatial standard deviation of the spatial kernel in x (in pixels, not in mm).
    double sigma_y,    // The standard deviation of the spatial kernel in y (in pixels).
    double sigma_r,    // The standard deviation of the range kernel (in pixel values).
    double *result     // Pointer to the output array (must have at least 'width*height' elements).
)
{
    if (data == NULL || result == NULL || width == 0 || height == 0 || !(sigma_x > 0) || !(sigma_y>0) || !(sigma_r > 0) || data == result) {
        return -1; // Invalid arguments

    }
    // Convert dimensions and calculate radii as signed integers (long) 
    // to allow safe math with negative spatial offsets without underflow. 
    const long w = (long)width;
    const long h = (long)height;
    const long radius_x = (long)ceil(3 * sigma_x);
    const long radius_y = (long)ceil(3 *sigma_y);

    const double two_sigma_x_squared = 2 * sigma_x * sigma_x;
    const double two_sigma_y_squared = 2 * sigma_y * sigma_y;
    const double two_sigma_r_squared = 2 * sigma_r * sigma_r;

    // 1. Allocate and compute lookup tables (lut) for spatial weights
    long lut_size_x = 2 * radius_x + 1;
    long lut_size_y = 2 * radius_y + 1;
    double *lut_x = (double *)malloc(lut_size_x * sizeof(double));
    double *lut_y = (double *)malloc(lut_size_y * sizeof(double));

    if (lut_x == NULL || lut_y == NULL) {
        free(lut_x);
        free(lut_y);
        return -1; // Memory allocation failed
    }

    // Precompute spatial weights for x
    for (long dx = -radius_x; dx <= radius_x; ++dx) {
        lut_x[dx + radius_x] = exp(-((double)(dx * dx) / two_sigma_x_squared));
    }

    // Precompute spatial weights for y
    for (long dy = -radius_y; dy <= radius_y; ++dy) {
        lut_y[dy + radius_y] = exp(-((double)(dy * dy) / two_sigma_y_squared));
    }
    
    // Main filtering loop
    for (long y = 0; y < h; ++y) {
        for (long x = 0; x < w; ++x) {
            const size_t index = (size_t)(y * w + x);
            const double pixel_value = data[index];
            double weighted_sum = 0.0;
            double weights = 0.0;

            for (long dy = -radius_y; dy <= radius_y; ++dy) {   // Loop over the y-offsets of the kernel
                for (long dx = -radius_x; dx <= radius_x; ++dx) {    // Loop over the x-offsets of the kernel
                    const long neighbor_x = x + dx;    
                    const long neighbor_y = y + dy;

                    // Boundary check to ensure neighbor is within image bounds
                    if (neighbor_x >= 0 && neighbor_x < w && neighbor_y >= 0 && neighbor_y < h) {
                        const size_t neighbor_index = (size_t)(neighbor_y * w + neighbor_x);
                        const double neighbor_value = data[neighbor_index];
                        const double diff = neighbor_value - pixel_value;
                        
                        // Combine precomputed spatial weight with dynamic range weight
                        const double spatial_weight = lut_x[dx + radius_x] * lut_y[dy + radius_y]; // Using precomputed spatial weights from lookup tables
                        const double range_weight = exp(-((diff) * (diff)) / (two_sigma_r_squared));
                        const double weight = spatial_weight * range_weight;
                        weighted_sum += weight * neighbor_value;
                        weights += weight;
                    }
                }
            }
            // Normalize and store the result
            result[index] = weighted_sum / weights; 
        }
    }
    free(lut_x);
    free(lut_y);

    return 0; // Success
}
