#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstddef>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <string>
#include <vector>

template <typename T>
struct Result {
    double runtime_ms;
    double checksum;
    double reference_checksum;
    double relative_error;
    bool correct;
};

template <typename T>
T* allocate_aligned(std::size_t n) {
    void* ptr = nullptr;

    if (posix_memalign(&ptr, 64, n * sizeof(T)) != 0) {
        throw std::bad_alloc();
    }

    return static_cast<T*>(ptr);
}

template <typename T>
void multiply_kernel(const T* a, const T* b, T* out, std::size_t n) {
    for (std::size_t i = 0; i < n; ++i) {
        out[i] = a[i] * b[i];
    }
}

template <typename T>
void saxpy_kernel(const T* a, const T* b, T* out,
                  T alpha, std::size_t n) {
    for (std::size_t i = 0; i < n; ++i) {
        out[i] = alpha * a[i] + b[i];
    }
}

template <typename T>
T dot_kernel(const T* a, const T* b, std::size_t n) {
    T sum = T(0);

    for (std::size_t i = 0; i < n; ++i) {
        sum += a[i] * b[i];
    }

    return sum;
}

double median(std::vector<double> values) {
    std::sort(values.begin(), values.end());

    const std::size_t middle = values.size() / 2;

    if (values.size() % 2 == 0) {
        return (values[middle - 1] + values[middle]) / 2.0;
    }

    return values[middle];
}

template <typename T>
Result<T> run_benchmark(const std::string& kernel,
                        std::size_t n,
                        int repetitions = 9) {
    T* a = allocate_aligned<T>(n);
    T* b = allocate_aligned<T>(n);
    T* out = allocate_aligned<T>(n);

    for (std::size_t i = 0; i < n; ++i) {
        a[i] = T(0.5) + T(i % 100) / T(100);
        b[i] = T(1.0) + T(i % 37) / T(50);
        out[i] = T(0);
    }

    const T alpha = T(1.25);

    // Run only the selected kernel. No checksum is calculated here.
    auto execute_kernel = [&]() -> T {
        if (kernel == "multiply") {
            multiply_kernel(a, b, out, n);
            return T(0);
        }

        if (kernel == "saxpy") {
            saxpy_kernel(a, b, out, alpha, n);
            return T(0);
        }

        return dot_kernel(a, b, n);
    };

    // Warm-up.
    volatile T warmup = execute_kernel();
    (void)warmup;

    // High-precision reference from the stored input values.
    long double reference = 0.0L;

    for (std::size_t i = 0; i < n; ++i) {
        if (kernel == "multiply" || kernel == "dot") {
            reference += static_cast<long double>(a[i]) *
                         static_cast<long double>(b[i]);
        } else {
            reference += static_cast<long double>(alpha) *
                         static_cast<long double>(a[i]) +
                         static_cast<long double>(b[i]);
        }
    }

    std::vector<double> times;
    times.reserve(repetitions);

    T dot_result = T(0);

    for (int r = 0; r < repetitions; ++r) {
        const auto start = std::chrono::steady_clock::now();

        const T result = execute_kernel();

        const auto stop = std::chrono::steady_clock::now();

        if (kernel == "dot") {
            dot_result = result;
        }

        times.push_back(
            std::chrono::duration<double, std::milli>(
                stop - start
            ).count()
        );
    }

    // Checksum outside the timed region for multiply and SAXPY.
    // Dot's reduction is part of the kernel and remains timed.
    long double checksum_ld = 0.0L;

    if (kernel == "multiply" || kernel == "saxpy") {
        for (std::size_t i = 0; i < n; ++i) {
            checksum_ld += static_cast<long double>(out[i]);
        }
    } else {
        checksum_ld = static_cast<long double>(dot_result);
    }

    const double checksum = static_cast<double>(checksum_ld);
    const double ref = static_cast<double>(reference);

    const double relative_error =
        std::abs(checksum - ref) / std::max(1.0, std::abs(ref));

    const bool correct =
        std::isfinite(checksum) &&
        std::isfinite(relative_error) &&
        relative_error < 1e-3;

    Result<T> result_data{
        median(times),
        checksum,
        ref,
        relative_error,
        correct
    };

    free(a);
    free(b);
    free(out);

    return result_data;
}

int main(int argc, char* argv[]) {
    if (argc != 4) {
        std::cerr << "Usage: " << argv[0]
                  << " <kernel> <N> <output.csv>\n"
                  << "Kernels: multiply, saxpy, dot\n";
        return 1;
    }

    const std::string kernel = argv[1];
    const std::size_t n = std::stoull(argv[2]);
    const std::string output_path = argv[3];

    if (n == 0 ||
        (kernel != "multiply" &&
         kernel != "saxpy" &&
         kernel != "dot")) {
        std::cerr << "Invalid kernel or input size\n";
        return 1;
    }

    try {
        const auto fp32 = run_benchmark<float>(kernel, n);
        const auto fp64 = run_benchmark<double>(kernel, n);

        std::ofstream csv(output_path);

        if (!csv) {
            std::cerr << "Could not open output file: "
                      << output_path << "\n";
            return 1;
        }

        csv << std::setprecision(12);
        csv << "kernel,N,precision,median_ms,checksum,"
               "reference_checksum,relative_error,correct\n";

        csv << kernel << "," << n << ",float32,"
            << fp32.runtime_ms << "," << fp32.checksum << ","
            << fp32.reference_checksum << ","
            << fp32.relative_error << ","
            << (fp32.correct ? "true" : "false") << "\n";

        csv << kernel << "," << n << ",float64,"
            << fp64.runtime_ms << "," << fp64.checksum << ","
            << fp64.reference_checksum << ","
            << fp64.relative_error << ","
            << (fp64.correct ? "true" : "false") << "\n";

        std::cout << kernel << " N=" << n << "\n";
        std::cout << "  FP32: " << fp32.runtime_ms
                  << " ms, relative error=" << fp32.relative_error
                  << ", correct=" << fp32.correct << "\n";
        std::cout << "  FP64: " << fp64.runtime_ms
                  << " ms, relative error=" << fp64.relative_error
                  << ", correct=" << fp64.correct << "\n";

    } catch (const std::exception& e) {
        std::cerr << "Benchmark failed: " << e.what() << "\n";
        return 1;
    }

    return 0;
}
