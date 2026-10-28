// Experiment 6 (timing-only): cost of "far" accesses in a dependent chain.
//
// Hardware cache-miss counters are not available on this system
// (perf_event_open -> EACCES), so this benchmark controls the *designed*
// fraction f of accesses that go to a large "far" buffer instead of
// measuring misses. Every access is a dependent load:
//   near: one of 256 cache lines in a 16 KiB buffer (stays L1-resident)
//   far : a pseudo-random cache line of a far buffer of F bytes
// The next address is chosen without branches (mask select) and includes
// (previous value >> 63), which is always 0 at runtime but forces each load
// to wait for the previous one. The near/far choice follows a Bresenham
// accumulator, so the far fraction is exact and evenly spread.
// Model: ns/access = T_near + f * (T_far - T_near). The fitted slope is the
// incremental cost of a far access; it is NOT a measured miss penalty.
//
// Output (CSV, no header): far_KiB,far_permille,thp,accesses,seconds,
//                           ns_per_access,anon_huge_KiB,checksum,cpu
#include <chrono>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <string>

#include "common.hpp"

int main(int argc, char** argv) {
    if (argc != 6) {
        std::cerr << "Usage: " << argv[0]
                  << " <far_KiB power of 2> <far_permille 0-1000> <accesses_millions>"
                     " <thp 0|1> <seed>\n";
        return 1;
    }
    const std::size_t far_kib = std::stoull(argv[1]);
    const unsigned permille = static_cast<unsigned>(std::stoul(argv[2]));
    const std::uint64_t accesses = std::stoull(argv[3]) * 1'000'000ULL;
    const bool thp = std::stoi(argv[4]) != 0;
    std::uint64_t state = std::stoull(argv[5]) | 1;

    const std::size_t far_lines = far_kib * 1024 / 64;
    if (far_lines == 0 || (far_lines & (far_lines - 1)) != 0 || permille > 1000) {
        std::cerr << "Invalid arguments.\n";
        return 1;
    }
    constexpr std::size_t kNearLines = 256;  // 16 KiB
    auto* near = static_cast<std::uint64_t*>(bench::alloc_buffer(kNearLines * 64, false));
    auto* far = static_cast<std::uint64_t*>(bench::alloc_buffer(far_kib * 1024, thp));
    const long huge_kib = bench::anon_huge_kib();
    constexpr std::size_t kWordsPerLine = 8;

    // Warm the near buffer and touch the far buffer once.
    std::uint64_t checksum = 0;
    for (std::size_t i = 0; i < kNearLines * kWordsPerLine; ++i) checksum += near[i];

    const std::uint64_t far_mask = far_lines - 1;
    std::uint64_t dep = 0;
    unsigned bres = 0;
    const auto t0 = std::chrono::steady_clock::now();
    for (std::uint64_t i = 0; i < accesses; ++i) {
        bres += permille;
        const std::uint64_t is_far = bres >= 1000;
        bres -= static_cast<unsigned>(is_far) * 1000;
        const std::uint64_t r = bench::xorshift64(state);
        const std::uint64_t far_word = ((r >> 20) & far_mask) * kWordsPerLine;
        const std::uint64_t near_word = (i & (kNearLines - 1)) * kWordsPerLine;
        const std::uint64_t m = 0 - is_far;  // all ones if far
        const std::uint64_t* base_near = near + near_word;
        const std::uint64_t* base_far = far + far_word;
        const auto addr = reinterpret_cast<const std::uint64_t*>(
            (reinterpret_cast<std::uintptr_t>(base_near) & ~m) |
            (reinterpret_cast<std::uintptr_t>(base_far) & m));
        const std::uint64_t v = addr[dep];
        checksum += v;
        dep = v >> 63;  // buffers hold zeros, so always 0
    }
    const double s = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();

    std::cout << far_kib << ',' << permille << ',' << thp << ',' << accesses << ','
              << std::fixed << std::setprecision(6) << s << ',' << std::setprecision(4)
              << s * 1e9 / accesses << ',' << huge_kib << ',' << checksum << ','
              << bench::current_cpu() << '\n';
    std::free(near);
    std::free(far);
    return 0;
}
