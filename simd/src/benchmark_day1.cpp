#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <random>
#include <string>
#include <vector>

using Clock = std::chrono::steady_clock;

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

int main(int argc, char** argv) {
    if (argc != 3) {
        std::cerr << "Usage: " << argv[0]
                  << " N output.csv\n";
        return 1;
    }

    const std::size_t n = std::stoull(argv[1]);
    const std::string output_file = argv[2];

    if (n == 0) {
        std::cerr << "N must be greater than zero\n";
        return 1;
    }

    std::vector<float> x(n);
    std::vector<float> y(n);
    std::vector<float> z(n);

    std::mt19937 rng(12345);
    std::uniform_real_distribution<float> dist(-1.0f, 1.0f);

    for (std::size_t i = 0; i < n; ++i) {
        x[i] = dist(rng);
        y[i] = dist(rng);
    }

    // Warm up the kernel before timing.
    multiply(x.data(), y.data(), z.data(), n);

    // Validate the result outside the timed region.
    for (std::size_t i = 0; i < n; ++i) {
        const float expected = x[i] * y[i];

        if (std::abs(z[i] - expected) > 1e-6f) {
            std::cerr << "Validation failed at index " << i << '\n';
            return 1;
        }
    }

    constexpr int repetitions = 9;
    std::vector<double> times_ms;
    times_ms.reserve(repetitions);

    volatile double checksum = 0.0;

    for (int r = 0; r < repetitions; ++r) {
        const auto start = Clock::now();

        multiply(x.data(), y.data(), z.data(), n);

        const auto end = Clock::now();

        const double elapsed_ms =
            std::chrono::duration<double, std::milli>(
                end - start
            ).count();

        times_ms.push_back(elapsed_ms);

        // Consume a result after timing to help prevent elimination.
        checksum = checksum + z[r % n];
    }

    std::sort(times_ms.begin(), times_ms.end());

    const double median_ms = times_ms[repetitions / 2];
    const double logical_bytes = 3.0 * n * sizeof(float);
    const double logical_gib =
        logical_bytes / (1024.0 * 1024.0 * 1024.0);

    const double gib_per_second =
        median_ms > 0.0
            ? logical_gib / (median_ms / 1000.0)
            : 0.0;

    std::ofstream out(output_file);

    if (!out) {
        std::cerr << "Cannot open output file: "
                  << output_file << '\n';
        return 1;
    }

    out << "N,median_ms,logical_GiB_per_s,checksum\n";
    out << std::setprecision(10)
        << n << ','
        << median_ms << ','
        << gib_per_second << ','
        << checksum << '\n';

    std::cout << "Elements: " << n << '\n';
    std::cout << "Median runtime: " << median_ms << " ms\n";
    std::cout << "Logical bandwidth: " << gib_per_second
              << " GiB/s\n";
    std::cout << "Checksum: " << checksum << '\n';
    std::cout << "Saved to: " << output_file << '\n';

    return 0;
}
