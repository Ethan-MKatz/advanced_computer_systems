// Experiment 3: read/write mix over a fixed working set.
//
// Each operation touches one random 8-byte word of a power-of-two buffer:
//   read  : acc += data[idx]
//   write : data[idx] = i            (plain store; the core still performs
//                                     a read-for-ownership of the line)
// Addresses come from an in-register xorshift64 generator, so no index array
// is streamed through the memory hierarchy during timing. The read/write
// decision uses a Bresenham accumulator: writes are spread evenly with a
// short period (10 for 30%, 2 for 50%), which keeps the branch predictable.
//
// mode = independent: addresses do not depend on loaded data, so many
//                     operations overlap -> throughput-bound measurement.
// mode = dependent  : each next address mixes in the previous read value
//                     (always 0 >> 63 == 0 at runtime, unknown to the CPU),
//                     so reads are serialized -> latency is exposed. Writes
//                     still retire into the store buffer without waiting.
//
// Output (CSV, no header): ws_KiB,write_pct,mode,ops,seconds,ns_per_op,
//                           mops_per_s,payload_GB_per_s,checksum,cpu
#include <chrono>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <string>

#include "common.hpp"

int main(int argc, char** argv) {
    if (argc != 6) {
        std::cerr << "Usage: " << argv[0]
                  << " <ws_KiB power of 2> <ops_millions> <write_pct 0-100>"
                     " <independent|dependent> <seed>\n";
        return 1;
    }
    const std::size_t kib = std::stoull(argv[1]);
    const std::uint64_t ops = std::stoull(argv[2]) * 1'000'000ULL;
    const unsigned write_pct = static_cast<unsigned>(std::stoul(argv[3]));
    const std::string mode = argv[4];
    std::uint64_t state = std::stoull(argv[5]) | 1;  // xorshift state must be nonzero

    const std::size_t words = kib * 1024 / sizeof(std::uint64_t);
    if (words == 0 || (words & (words - 1)) != 0 || write_pct > 100 ||
        (mode != "independent" && mode != "dependent")) {
        std::cerr << "Invalid arguments.\n";
        return 1;
    }
    const std::uint64_t mask = words - 1;
    const bool dependent = mode == "dependent";

    auto* data = static_cast<std::uint64_t*>(bench::alloc_buffer(kib * 1024, false));

    // Warm-up: one untimed sweep of reads over the buffer.
    std::uint64_t acc = 0;
    for (std::size_t i = 0; i < words; ++i) acc += data[i];

    std::uint64_t dep = 0;      // carries the data dependency in dependent mode
    unsigned bres = 0;          // Bresenham accumulator for the write fraction

    const auto start = std::chrono::steady_clock::now();
    for (std::uint64_t i = 0; i < ops; ++i) {
        const std::uint64_t r = bench::xorshift64(state);
        const std::uint64_t idx = ((r >> 11) ^ dep) & mask;
        bres += write_pct;
        if (bres >= 100) {
            bres -= 100;
            data[idx] = i;
        } else {
            const std::uint64_t v = data[idx];
            acc += v;
            if (dependent) dep = v >> 63;   // stored values are < 2^63, so 0
        }
    }
    const auto stop = std::chrono::steady_clock::now();
    bench::clobber(data);

    std::uint64_t checksum = acc;
    for (std::size_t i = 0; i < words; i += words / 64 + 1) checksum += data[i];

    const double seconds = std::chrono::duration<double>(stop - start).count();
    std::cout << kib << ',' << write_pct << ',' << mode << ',' << ops << ','
              << std::fixed << std::setprecision(6) << seconds << ','
              << std::setprecision(4) << seconds * 1e9 / ops << ','
              << ops / seconds / 1e6 << ',' << ops * 8.0 / seconds / 1e9 << ','
              << checksum << ',' << bench::current_cpu() << '\n';
    std::free(data);
    return 0;
}
