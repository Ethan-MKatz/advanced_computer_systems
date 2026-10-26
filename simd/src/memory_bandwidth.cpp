#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstddef>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <vector>

#ifdef __GNUC__
#define NOINLINE __attribute__((noinline))
#else
#define NOINLINE
#endif

NOINLINE void triad(float* a, const float* b, const float* c,
                    std::size_t n, float scalar) {
    for (std::size_t i = 0; i < n; ++i) {
        a[i] = b[i] + scalar * c[i];
    }
}

int main(int argc, char** argv) {
    // Default: 32 million float elements per array (~128 MiB per array).
    const std::size_t n =
        argc > 1 ? std::stoull(argv[1]) : 32ULL * 1024 * 1024;
    const int repetitions = argc > 2 ? std::stoi(argv[2]) : 10;

    if (n == 0 || repetitions < 1) {
        std::cerr << "Usage: " << argv[0] << " [N] [repetitions]\n";
        return 1;
    }

    std::vector<float> a(n), b(n), c(n);

    for (std::size_t i = 0; i < n; ++i) {
        a[i] = 0.0f;
        b[i] = 1.0f + static_cast<float>(i % 100) * 0.01f;
        c[i] = 2.0f + static_cast<float>(i % 50) * 0.02f;
    }

    constexpr float scalar = 3.0f;

    // Warm up before measuring.
    triad(a.data(), b.data(), c.data(), n, scalar);

    std::vector<double> times_ms;
    times_ms.reserve(repetitions);

    for (int r = 0; r < repetitions; ++r) {
        const auto start = std::chrono::steady_clock::now();

        triad(a.data(), b.data(), c.data(), n, scalar);

        const auto stop = std::chrono::steady_clock::now();
        const double ms =
            std::chrono::duration<double, std::milli>(stop - start).count();

        times_ms.push_back(ms);
    }

    std::sort(times_ms.begin(), times_ms.end());
    const double median_ms = times_ms[times_ms.size() / 2];

    // Logical traffic: 2 float reads + 1 float write per element.
    // This is an estimate of useful data traffic, not measured DRAM traffic.
    const double logical_bytes = 3.0 * sizeof(float) * n;
    const double seconds = median_ms / 1000.0;
    const double bandwidth_gib_s =
        logical_bytes / seconds / (1024.0 * 1024 * 1024);

    const double checksum =
        std::accumulate(a.begin(), a.end(), 0.0);

    const double expected_first =
        static_cast<double>(b[0]) + scalar * static_cast<double>(c[0]);
    const bool correct = std::abs(a[0] - expected_first) < 1e-5;

    std::cout << std::fixed << std::setprecision(6);
    std::cout << "N: " << n << '\n';
    std::cout << "Repetitions: " << repetitions << '\n';
    std::cout << "Median runtime (ms): " << median_ms << '\n';
    std::cout << "Logical bandwidth (GiB/s): " << bandwidth_gib_s << '\n';
    std::cout << "Checksum: " << checksum << '\n';
    std::cout << "Correctness check: " << (correct ? "PASS" : "FAIL") << '\n';

    return correct ? 0 : 1;
}
