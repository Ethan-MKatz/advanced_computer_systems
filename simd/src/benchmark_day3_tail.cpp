#include <algorithm>
#include <chrono>
#include <fstream>
#include <iostream>
#include <numeric>
#include <string>
#include <vector>

void multiply(const float* a, const float* b, float* out, size_t n) {
    for (size_t i = 0; i < n; ++i) {
        out[i] = a[i] * b[i];
    }
}

double median(std::vector<double> times) {
    std::sort(times.begin(), times.end());
    return times[times.size() / 2];
}

int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cerr << "Usage: " << argv[0] << " <base_N> <output.csv>\n";
        return 1;
    }

    const size_t base_n = std::stoull(argv[1]);
    const std::string output_path = argv[2];

    if (base_n == 0) {
        std::cerr << "Base N must be positive\n";
        return 1;
    }

    std::ofstream csv(output_path);
    if (!csv) {
        std::cerr << "Cannot open output file: " << output_path << "\n";
        return 1;
    }

    csv << "N,tail_remainder,runtime_ms,checksum\n";

    constexpr int repetitions = 21;

    for (size_t tail = 0; tail < 8; ++tail) {
        const size_t n = base_n + tail;

        std::vector<float> a(n), b(n), out(n);

        for (size_t i = 0; i < n; ++i) {
            a[i] = 1.0f + float(i % 17) * 0.01f;
            b[i] = 2.0f + float(i % 13) * 0.02f;
        }

        multiply(a.data(), b.data(), out.data(), n);

        std::vector<double> times;

        for (int r = 0; r < repetitions; ++r) {
            auto start = std::chrono::steady_clock::now();
            multiply(a.data(), b.data(), out.data(), n);
            auto end = std::chrono::steady_clock::now();

            times.push_back(
                std::chrono::duration<double, std::milli>(
                    end - start
                ).count()
            );
        }

        const double checksum = std::accumulate(
            out.begin(), out.end(), 0.0
        );

        const double runtime = median(times);

        csv << n << "," << tail << "," << runtime
            << "," << checksum << "\n";

        std::cout << "N=" << n
                  << " tail=" << tail
                  << " runtime_ms=" << runtime
                  << " checksum=" << checksum << "\n";
    }

    return 0;
}
