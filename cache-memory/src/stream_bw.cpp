// Streaming-bandwidth benchmark (experiments 5b and 8a).
//
// read : sum all 8-byte words of the buffer (4 independent accumulators, the
//        compiler vectorizes this with -O3 -march=native)
// write: store a pass-dependent value to every word (data[i] = v ^ i, which
//        keeps the compiler from turning it into memset / non-temporal stores)
// Bytes counted = buffer bytes x passes ("software-counted bytes"): one read
// or one write of each word. For writes the hardware additionally performs a
// read-for-ownership and an eventual write-back, which are NOT counted.
//
// sweep mode  : passes = max(min_passes, target_bytes / buffer); prints one
//               aggregate row: mode,ws_KiB,passes,seconds,GB_per_s,checksum,cpu
// Both modes busy-wait 200 ms first so the core clock has ramped up.
// perpass mode: page-faults the buffer in, evicts it from the caches by
//               reading a separate 64 MiB buffer, then times each pass
//               separately; prints pass,seconds,GB_per_s rows (pass 1 = cold).
#include <chrono>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <string>

#include "common.hpp"

using Clock = std::chrono::steady_clock;

static std::uint64_t read_pass(const std::uint64_t* d, std::size_t n) {
    std::uint64_t a0 = 0, a1 = 0, a2 = 0, a3 = 0;
    for (std::size_t i = 0; i < n; i += 4) {
        a0 += d[i];
        a1 += d[i + 1];
        a2 += d[i + 2];
        a3 += d[i + 3];
    }
    return a0 + a1 + a2 + a3;
}

static void write_pass(std::uint64_t* d, std::size_t n, std::uint64_t v) {
    for (std::size_t i = 0; i < n; ++i) d[i] = v ^ i;
    bench::clobber(d);
}

static std::uint64_t run_pass(const std::string& mode, std::uint64_t* d, std::size_t n,
                              std::uint64_t pass) {
    if (mode == "read") {
        const std::uint64_t s = read_pass(d, n);
        bench::clobber(d);
        return s;
    }
    write_pass(d, n, pass);
    return d[pass % n];
}

int main(int argc, char** argv) {
    if (argc != 6) {
        std::cerr << "Usage: " << argv[0]
                  << " <sweep|perpass> <read|write> <ws_KiB> <target_MiB or passes> <thp 0|1>\n";
        return 1;
    }
    const std::string kind = argv[1];
    const std::string mode = argv[2];
    const std::size_t kib = std::stoull(argv[3]);
    const std::size_t arg4 = std::stoull(argv[4]);
    const bool thp = std::stoi(argv[5]) != 0;
    const std::size_t bytes = kib * 1024;
    const std::size_t n = bytes / sizeof(std::uint64_t);
    if (n == 0 || n % 4 != 0 || (mode != "read" && mode != "write") ||
        (kind != "sweep" && kind != "perpass")) {
        std::cerr << "Invalid arguments.\n";
        return 1;
    }

    auto* d = static_cast<std::uint64_t*>(bench::alloc_buffer(bytes, thp));
    for (std::size_t i = 0; i < n; ++i) d[i] = i;
    std::uint64_t checksum = 0;
    bench::spin_warmup(200);

    if (kind == "sweep") {
        const std::size_t min_passes = 5;
        std::size_t passes = arg4 * 1024 * 1024 / bytes;
        if (passes < min_passes) passes = min_passes;
        checksum += run_pass(mode, d, n, 0);  // warm-up pass
        const auto t0 = Clock::now();
        for (std::size_t p = 1; p <= passes; ++p) checksum += run_pass(mode, d, n, p);
        const double s = std::chrono::duration<double>(Clock::now() - t0).count();
        std::cout << mode << ',' << kib << ',' << passes << ',' << std::fixed
                  << std::setprecision(6) << s << ',' << std::setprecision(3)
                  << static_cast<double>(bytes) * passes / s / 1e9 << ',' << checksum << ','
                  << bench::current_cpu() << '\n';
    } else {
        const std::size_t passes = arg4;
        const std::size_t evict_bytes = 64u << 20;
        auto* ev = static_cast<std::uint64_t*>(bench::alloc_buffer(evict_bytes, thp));
        checksum += read_pass(ev, evict_bytes / sizeof(std::uint64_t));
        for (std::size_t p = 1; p <= passes; ++p) {
            const auto t0 = Clock::now();
            checksum += run_pass(mode, d, n, p);
            const double s = std::chrono::duration<double>(Clock::now() - t0).count();
            std::cout << p << ',' << std::fixed << std::setprecision(9) << s << ','
                      << std::setprecision(3) << bytes / s / 1e9 << '\n';
        }
        std::cerr << "checksum " << checksum << " cpu " << bench::current_cpu() << '\n';
        std::free(ev);
    }
    std::free(d);
    return 0;
}
