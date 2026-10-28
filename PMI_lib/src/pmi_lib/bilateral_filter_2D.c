#include <stddef.h>  // Provides size_t
#include <math.h>    // Provides exp() and ceil function

//  Applies a 2-dimensional bilateral filter.
//  Returns 0 on success, -1 on invalid arguments.
int bilateral_filter(
    double *data,    // Pointer to a 1-dimensional array.
    size_t width,   // A 2D image has a width and height.
    size_t height,    // A 2D image has a width and height.
    double sigma_x,  // The spatial standard deviation of the spatial kernel in x (in pixels, not in mm).
    double sigma_y, // The standard deviation of the spatial kernel in y (in pixels).
    double sigma_r,  // The standard deviation of the range kernel (in pixel values).
    double *result   // Pointer to the output array (must have at least 'width*height' elements).
)
{
    if (data == NULL || result == NULL || width == 0 || height == 0 || !(sigma_x > 0) || !(sigma_y>0) || !(sigma_r > 0) || data == result) {
        return -1; // Invalid arguments

    }
    // Since size_t is an unsigned type it doesnt represent negative numbers. This is a problem, because
    // if i < j, then i - j will wrap around to a huge positive number. Indices need to first be converted
    // to double or signed types such as long, before being subtracted to give the true difference. This
    // allows the filter to use the correct signed distance between 2 pixels.
    const long w = (long)width;
    const long h = (long)height;
    const long radius_x = (long)ceil(3 * sigma_x);
    const long radius_y = (long)ceil(3 *sigma_y);
    const double two_sigma_x_squared = 2 * sigma_x * sigma_x;
    const double two_sigma_y_squared = 2 * sigma_y * sigma_y;
    const double two_sigma_r_squared = 2 * sigma_r * sigma_r;

    for (long y = 0; y < h; ++y) {
        for (long x = 0; x < w; ++x) {
            const size_t index = (size_t)(y * w + x);
            const double pixel_value = data[index];
            double weighted_sum = 0.0;
            double weights = 0.0;
            for (long dy = -radius_y; dy <= radius_y; ++dy) {   // Since offsets run from -radius to +radius, offsets and radii must be signed (long) to avoid overflow.
                for (long dx = -radius_x; dx <= radius_x; ++dx) {    // With unsigned types, -radius would wrap around to a large positive number, meaning that the loop wouldnt run.
                    const long neighbor_x = x + dx;    //Using signed coordinates allows a neighbour on the edge to be a real negative number so the bounds check can be done correctly.
                    const long neighbor_y = y + dy;
                    if (neighbor_x >= 0 && neighbor_x < w && neighbor_y >= 0 && neighbor_y < h) {
                        const size_t neighbor_index = (size_t)(neighbor_y * w + neighbor_x);
                        const double neighbor_value = data[neighbor_index];
                        const double diff = neighbor_value - pixel_value;
                        const double spatial_weight = exp(-((double)(dx * dx) / (two_sigma_x_squared) + (double)(dy * dy) / (two_sigma_y_squared)));
                        const double range_weight = exp(-((diff) * (diff)) / (two_sigma_r_squared));
                        const double weight = spatial_weight * range_weight;
                        weighted_sum += weight * neighbor_value;
                        weights += weight;
                    }
                }
            }
            result[index] = weighted_sum / weights; // Normalizing result
        }
    }
    return 0; // Success
}