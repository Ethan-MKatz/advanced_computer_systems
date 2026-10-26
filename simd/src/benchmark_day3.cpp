#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <string>
#include <vector>

#ifdef __linux__
#include <sys/mman.h>
#endif

using Clock = std::chrono::steady_clock;

// Allocate memory with a specified alignment.
float* allocate_aligned(std::size_t n) {
    void* ptr = nullptr;

    if (posix_memalign(&ptr, 64, n * sizeof(float)) != 0) {
        throw std::bad_alloc();
    }

    return static_cast<float*>(ptr);
}

// Elementwise multiplication with configurable stride.
// The output is compact: one result per selected input element.
void multiply_stride(
    const float* a,
    const float* b,
    float* out,
    std::size_t n,
    std::size_t stride
) {
    for (std::size_t i = 0; i < n; ++i) {
        out[i] = a[i * stride] * b[i * stride];
    }
}

// Measure median execution time in milliseconds.
template <typename Function>
double median_ms(Function function, int repetitions =  9) {
    std::vector<double> times;
    times.reserve(repetitions);

    function(); // Warm-up

    for (int r = 0; r < repetitions; ++r) {
        auto start = Clock::now();
        function();
        auto end = Clock::now();

        times.push_back(
            std::chrono::duration<double, std::milli>(end - start).count()
        );
    }

    std::sort(times.begin(), times.end());
    return times[times.size() / 2];
}

int main(int argc, char* argv[]) {
    if (argc != 4) {
        std::cerr
            << "Usage: " << argv[0]
            << " <N> <stride> <output.csv>\n";
        return 1;
    }

    const std::size_t n = std::stoull(argv[1]);
    const std::size_t stride = std::stoull(argv[2]);
    const std::string output_path = argv[3];

    if (n == 0 || stride == 0) {
        std::cerr << "N and stride must be greater than zero.\n";
        return 1;
    }

    const std::size_t allocated_n = n * stride + 16;

    float* a = allocate_aligned(allocated_n);
    float* b = allocate_aligned(allocated_n);
    float* out = allocate_aligned(n);

    for (std::size_t i = 0; i < allocated_n; ++i) {
        a[i] = 1.0f + static_cast<float>(i % 17) * 0.01f;
        b[i] = 2.0f + static_cast<float>(i % 13) * 0.01f;
    }

    std::fill(out, out + n, 0.0f);

    multiply_stride(a, b, out, n, stride);

    // Validate the results before timing.
    bool correct = true;

    for (std::size_t i = 0; i < n; ++i) {
        const float expected = a[i * stride] * b[i * stride];

        if (std::fabs(out[i] - expected) > 1e-6f) {
            correct = false;
            break;
        }
    }

    if (!correct) {
        std::cerr << "Correctness validation failed.\n";
        std::free(a);
        std::free(b);
        std::free(out);
        return 1;
    }

    const double runtime_ms = median_ms([&]() {
        multiply_stride(a, b, out, n, stride);
    }, 9);

    double checksum = 0.0;
    for (std::size_t i = 0; i < n; ++i) {
        checksum += out[i];
    }

    std::ofstream csv(output_path);

    if (!csv) {
        std::cerr << "Could not open output CSV: " << output_path << "\n";
        std::free(a);
        std::free(b);
        std::free(out);
        return 1;
    }

    csv << "N,stride,runtime_ms,checksum,correct\n";
    csv << n << ","
        << stride << ","
        << std::setprecision(10) << runtime_ms << ","
        << checksum << ","
        << (correct ? "true" : "false") << "\n";

    std::cout << "N=" << n
              << " stride=" << stride
              << " median_ms=" << runtime_ms
              << " checksum=" << checksum
              << " correct=" << (correct ? "yes" : "no")
              << "\n";

    std::free(a);
    std::free(b);
    std::free(out);

    return 0;
}
