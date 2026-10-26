#include <cstddef>

void multiply(
    const float* x,
    const float* y,
    float* z,
    std::size_t n
) {
    for (std::size_t i = 0; i < n; ++i) {
        z[i] = x[i] * y[i];
    }
}
