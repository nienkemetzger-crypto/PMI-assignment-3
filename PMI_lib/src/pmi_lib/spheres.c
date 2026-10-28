#include <stddef.h>

int add_sphere(
    double *data,  // Pointer to the input array.
    size_t nx,     // Number of pixels in the x-dimension.
    size_t ny,     // Number of pixels in the y-dimension.
    size_t nz,     // Number of pixels in the z-dimension.
    double sx,     // Spacing in x in mm.
    double sy,     // Spacing in y in mm.
    double sz,     // Spacing in z in mm.
    double radius, // Radius in mm
    double value   // Value to add.
) {
    double cx = (nx - 1) / 2.0;
    double cy = (ny - 1) / 2.0;
    double cz = (nz - 1) / 2.0;
    double radius_sq = radius * radius;

    for (size_t z = 0; z < nz; z++) {
        for (size_t y = 0; y < ny; y++) {
            for (size_t x = 0; x < nx; x++) {
                // Cast size_t to double before subtraction to prevent underflow with unsigned types[cite: 3]
                double dx = ((double)x - cx) * sx;
                double dy = ((double)y - cy) * sy;
                double dz = ((double)z - cz) * sz;

                if ((dx*dx + dy*dy + dz*dz) <= radius_sq) {
                    size_t index = z * ny * nx + y * nx + x;
                    data[index] += value;
                }
            }
        }
    }
    return 0;
}