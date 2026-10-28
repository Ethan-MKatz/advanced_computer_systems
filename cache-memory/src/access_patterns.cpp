#include <algorithm>
#include <chrono>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <random>
#include <string>
#include <vector>

using Clock = std::chrono::steady_clock;

int main(int argc, char** argv) {
    if (argc != 4) {
        std::cerr << "Usage: " << argv[0]
                  << " <working_set_MiB> <passes> <seed>\n";
        return 1;
    }

    const std::size_t mib = std::stoull(argv[1]);
    const std::size_t passes = std::stoull(argv[2]);
    const unsigned seed = static_cast<unsigned>(std::stoul(argv[3]));

    if (mib == 0 || passes == 0) {
        std::cerr << "Working set and passes must be positive.\n";
        return 1;
    }

    const std::size_t bytes = mib * 1024ULL * 1024ULL;
    const std::size_t elements = bytes / sizeof(std::uint64_t);
    std::vector<std::uint64_t> data(elements, 1);

    std::cout << "pattern,stride_bytes,working_set_MiB,passes,"
                 "elapsed_seconds,effective_GB_per_second,checksum\n";

    for (const std::string pattern : {"sequential", "random"}) {
        for (const std::size_t stride_bytes : {64, 256, 1024}) {
            const std::size_t stride_words =
                stride_bytes / sizeof(std::uint64_t);

            std::vector<std::size_t> order;
            for (std::size_t i = 0; i < elements; i += stride_words) {
                order.push_back(i);
            }

            if (pattern == "random") {
                std::mt19937 rng(seed + static_cast<unsigned>(stride_bytes));
                std::shuffle(order.begin(), order.end(), rng);
            }

            std::fill(data.begin(), data.end(), 1);

            // Warm up one complete traversal.
            std::uint64_t warmup_checksum = 0;
            for (const std::size_t index : order) {
                warmup_checksum += data[index];
            }

            std::uint64_t checksum = warmup_checksum;
            const auto start = Clock::now();

            for (std::size_t pass = 0; pass < passes; ++pass) {
                for (const std::size_t index : order) {
                    data[index] += 1;
                    checksum += data[index];
                }
            }

            const auto stop = Clock::now();
            const double seconds =
                std::chrono::duration<double>(stop - start).count();

            // Effective bytes: 8-byte load + 8-byte store per element
            // updated. This is a software-level estimate, not DRAM traffic.
            const double accesses =
                static_cast<double>(order.size()) * passes;
            const double effective_bytes = accesses * 16.0;
            const double effective_gb_s =
                effective_bytes / seconds / 1e9;

            std::cout << pattern << ','
                      << stride_bytes << ','
                      << mib << ','
                      << passes << ','
                      << std::fixed << std::setprecision(6)
                      << seconds << ','
                      << effective_gb_s << ','
                      << checksum << '\n';
        }
    }

    return 0;
}
