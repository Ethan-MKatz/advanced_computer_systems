#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstddef>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <random>
#include <string>
#include <vector>

using Clock = std::chrono::steady_clock;

// Kernel 1: Elementwise multiplication
void elementwise_multiply(
    const float* x,
    const float* y,
    float* z,
    std::size_t n
) {
    for (std::size_t i = 0; i < n; ++i) {
        z[i] = x[i] * y[i];
    }
}

// Kernel 2: SAXPY: y[i] = a * x[i] + y[i]
void saxpy(
    float a,
    const float* x,
    float* y,
    std::size_t n
) {
    for (std::size_t i = 0; i < n; ++i) {
        y[i] = a * x[i] + y[i];
    }
}

// Kernel 3: Dot product (reduction)
float dot_product(
    const float* x,
    const float* y,
    std::size_t n
) {
    float sum = 0.0f;

    for (std::size_t i = 0; i < n; ++i) {
        sum += x[i] * y[i];
    }

    return sum;
}

int main(int argc, char** argv) {
    if (argc != 4) {
        std::cerr
            << "Usage: " << argv[0]
            << " <kernel> <N> <output.csv>\n"
            << "Kernels: multiply, saxpy, dot\n";
        return 1;
    }

    const std::string kernel = argv[1];
    const std::size_t n = std::stoull(argv[2]);
    const std::string output_file = argv[3];

    if (n == 0) {
        std::cerr << "N must be greater than zero\n";
        return 1;
    }

    if (kernel != "multiply" &&
        kernel != "saxpy" &&
        kernel != "dot") {
        std::cerr << "Unknown kernel: " << kernel << '\n';
        return 1;
    }

    // Allocate arrays.
    std::vector<float> x(n);
    std::vector<float> y(n);
    std::vector<float> z(n, 0.0f);

    // Preserve initial values so every SAXPY repetition
    // starts from the same input.
    std::vector<float> y_initial(n);

    // Deterministic input data for reproducibility.
    std::mt19937 rng(12345);
    std::uniform_real_distribution<float> dist(-1.0f, 1.0f);

    for (std::size_t i = 0; i < n; ++i) {
        x[i] = dist(rng);
        y[i] = dist(rng);
        y_initial[i] = y[i];
    }

    constexpr float a = 2.0f;
    constexpr int repetitions = 9;

    // Warm up the selected kernel.
    if (kernel == "multiply") {
        elementwise_multiply(x.data(), y.data(), z.data(), n);
    } else if (kernel == "saxpy") {
        saxpy(a, x.data(), y.data(), n);
    } else {
        const float warmup = dot_product(x.data(), y.data(), n);
        (void)warmup;
    }

    // Validate correctness outside the timed region.
    if (kernel == "multiply") {
        for (std::size_t i = 0; i < n; ++i) {
            const float expected = x[i] * y_initial[i];

            if (std::abs(z[i] - expected) > 1e-6f) {
                std::cerr
                    << "Multiply validation failed at index "
                    << i << '\n';
                return 1;
            }
        }
    } else if (kernel == "saxpy") {
        for (std::size_t i = 0; i < n; ++i) {
            const float expected = a * x[i] + y_initial[i];

            if (std::abs(y[i] - expected) >
                1e-5f * std::max(1.0f, std::abs(expected))) {
                std::cerr
                    << "SAXPY validation failed at index "
                    << i << '\n';
                return 1;
            }
        }
    } else {
        double reference = 0.0;

        for (std::size_t i = 0; i < n; ++i) {
            reference +=
                static_cast<double>(x[i]) *
                static_cast<double>(y_initial[i]);
        }

        const double actual =
            static_cast<double>(
                dot_product(x.data(), y_initial.data(), n)
            );

        const double tolerance =
            1e-4 * std::max(1.0, std::abs(reference));

        if (std::abs(actual - reference) > tolerance) {
            std::cerr
                << "Dot product validation failed. Expected "
                << reference << ", got " << actual << '\n';
            return 1;
        }
    }

    // Benchmark each repetition and report the median.
    std::vector<double> times_ms;
    times_ms.reserve(repetitions);

    double checksum = 0.0;

    for (int r = 0; r < repetitions; ++r) {
        // Reset SAXPY input outside the timed region.
        if (kernel == "saxpy") {
            y = y_initial;
        }

        const auto start = Clock::now();

        if (kernel == "multiply") {
            elementwise_multiply(
                x.data(), y.data(), z.data(), n
            );
        } else if (kernel == "saxpy") {
            saxpy(a, x.data(), y.data(), n);
        } else {
            checksum = dot_product(
                x.data(), y.data(), n
            );
        }

        const auto end = Clock::now();

        const double elapsed_ms =
            std::chrono::duration<double, std::milli>(
                end - start
            ).count();

        times_ms.push_back(elapsed_ms);

        // Consume output after timing.
        if (kernel == "multiply") {
            checksum += z[static_cast<std::size_t>(r) % n];
        } else if (kernel == "saxpy") {
            checksum += y[static_cast<std::size_t>(r) % n];
        }
    }

    std::sort(times_ms.begin(), times_ms.end());

    const double median_ms = times_ms[repetitions / 2];

    // Logical data traffic per element:
    // multiply: read x, read y, write z = 12 bytes
    // SAXPY: read x, read y, write y = 12 bytes
    // dot: read x and y = 8 bytes
    const double bytes_per_element =
        (kernel == "dot") ? 2.0 * sizeof(float)
                          : 3.0 * sizeof(float);

    const double logical_bytes =
        static_cast<double>(n) * bytes_per_element;

    const double logical_gib =
        logical_bytes / (1024.0 * 1024.0 * 1024.0);

    const double gib_per_second =
        median_ms > 0.0
            ? logical_gib / (median_ms / 1000.0)
            : 0.0;

    // FLOPs per element:
    // multiply: 1
    // SAXPY: 2
    // dot: 2
    const double flops_per_element =
        (kernel == "multiply") ? 1.0 : 2.0;

    const double total_flops =
        static_cast<double>(n) * flops_per_element;

    const double gflops_per_second =
        median_ms > 0.0
            ? total_flops / (median_ms / 1000.0) / 1e9
            : 0.0;

    std::ofstream out(output_file);

    if (!out) {
        std::cerr << "Cannot open output file: "
                  << output_file << '\n';
        return 1;
    }

    out << "kernel,N,median_ms,logical_GiB_per_s,"
           "GFLOP_per_s,checksum\n";

    out << std::setprecision(10)
        << kernel << ','
        << n << ','
        << median_ms << ','
        << gib_per_second << ','
        << gflops_per_second << ','
        << checksum << '\n';

    std::cout << "Kernel: " << kernel << '\n';
    std::cout << "Elements: " << n << '\n';
    std::cout << "Median runtime: " << median_ms << " ms\n";
    std::cout << "Logical bandwidth: "
              << gib_per_second << " GiB/s\n";
    std::cout << "Performance: "
              << gflops_per_second << " GFLOP/s\n";
    std::cout << "Checksum: " << checksum << '\n';
    std::cout << "Saved to: " << output_file << '\n';

    return 0;
}
