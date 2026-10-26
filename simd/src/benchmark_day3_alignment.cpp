#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstddef>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <numeric>
#include <string>
#include <vector>

float* allocate_aligned(std::size_t n) {
    void* ptr = nullptr;
    if (posix_memalign(&ptr, 64, n * sizeof(float)) != 0) {
        std::cerr << "Memory allocation failed\n";
        std::exit(1);
    }
    return static_cast<float*>(ptr);
}

void multiply(const float* a, const float* b, float* out,
              std::size_t n) {
    for (std::size_t i = 0; i < n; ++i) {
        out[i] = a[i] * b[i];
    }
}

double median(std::vector<double> values) {
    std::sort(values.begin(), values.end());
    return values[values.size() / 2];
}

int main(int argc, char* argv[]) {
    if (argc != 4) {
        std::cerr << "Usage: " << argv[0]
                  << " <N> <offset_floats> <output.csv>\n";
        return 1;
    }

    const std::size_t n = std::stoull(argv[1]);
    const std::size_t offset = std::stoull(argv[2]);
    const std::string output_path = argv[3];

    if (n == 0 || offset > 15) {
        std::cerr << "N must be positive and offset must be 0-15 floats\n";
        return 1;
    }

    float* a_base = allocate_aligned(n + offset);
    float* b_base = allocate_aligned(n + offset);
    float* out = allocate_aligned(n);

    float* a = a_base + offset;
    float* b = b_base + offset;

    for (std::size_t i = 0; i < n + offset; ++i) {
        a_base[i] = 1.0f + static_cast<float>(i % 17) * 0.01f;
        b_base[i] = 2.0f + static_cast<float>(i % 13) * 0.02f;
    }

    // Warm-up and correctness reference.
    multiply(a, b, out, n);

    double reference_checksum = 0.0;
    for (std::size_t i = 0; i < n; ++i) {
        reference_checksum += static_cast<double>(a[i]) * b[i];
    }

    double checksum = 0.0;
    for (std::size_t i = 0; i < n; ++i) {
        checksum += out[i];
    }

    const bool correct =
        std::abs(checksum - reference_checksum) <=
        1e-5 * std::max(1.0, std::abs(reference_checksum));

    std::vector<double> times_ms;
    constexpr int repetitions = 9;

    for (int r = 0; r < repetitions; ++r) {
        const auto start = std::chrono::steady_clock::now();
        multiply(a, b, out, n);
        const auto end = std::chrono::steady_clock::now();

        const double elapsed =
            std::chrono::duration<double, std::milli>(end - start).count();
        times_ms.push_back(elapsed);
    }

    // Consume output after timing to ensure the result is used.
    checksum = 0.0;
    for (std::size_t i = 0; i < n; ++i) {
        checksum += out[i];
    }

    std::ofstream csv(output_path);
    if (!csv) {
        std::cerr << "Could not open output file: " << output_path << "\n";
        free(a_base);
        free(b_base);
        free(out);
        return 1;
    }

    csv << "N,offset_floats,runtime_ms,checksum,correct\n";
    csv << n << "," << offset << "," << median(times_ms) << ","
        << checksum << "," << (correct ? "true" : "false") << "\n";

    std::cout << "N=" << n
              << " offset=" << offset << " floats ("
              << offset * sizeof(float) << " bytes)"
              << " median_ms=" << median(times_ms)
              << " checksum=" << checksum
              << " correct=" << (correct ? "true" : "false")
              << "\n";

    free(a_base);
    free(b_base);
    free(out);

    return correct ? 0 : 1;
}
