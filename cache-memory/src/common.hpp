// Shared helpers for the cache-memory benchmarks: buffer allocation with
// optional transparent huge pages, and nonprivileged run metadata
// (CPU the thread ran on, minor page faults, AnonHugePages backing).
#pragma once

#include <sched.h>
#include <sys/mman.h>
#include <sys/resource.h>

#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iostream>
#include <string>

namespace bench {

constexpr std::size_t kHugePage = 2u << 20;

// Allocate `bytes` aligned to 2 MiB. With `thp`, request transparent huge
// pages via madvise(MADV_HUGEPAGE) (allowed for unprivileged processes when
// /sys/kernel/mm/transparent_hugepage/enabled is "madvise"); otherwise ask
// for regular 4 KiB pages with MADV_NOHUGEPAGE so the baseline is explicit.
// The buffer is written once so every page is faulted in before timing.
inline void* alloc_buffer(std::size_t bytes, bool thp) {
    const std::size_t rounded = (bytes + kHugePage - 1) / kHugePage * kHugePage;
    void* p = std::aligned_alloc(kHugePage, rounded);
    if (p == nullptr) {
        std::cerr << "allocation of " << rounded << " bytes failed\n";
        std::exit(1);
    }
    madvise(p, rounded, thp ? MADV_HUGEPAGE : MADV_NOHUGEPAGE);
    std::memset(p, 0, rounded);
    return p;
}

inline long minor_faults() {
    rusage ru{};
    getrusage(RUSAGE_SELF, &ru);
    return ru.ru_minflt;
}

// AnonHugePages (KiB) currently mapped by this process.
inline long anon_huge_kib() {
    std::ifstream f("/proc/self/smaps_rollup");
    std::string key;
    long value = -1;
    while (f >> key) {
        if (key == "AnonHugePages:") {
            f >> value;
            return value;
        }
    }
    return -1;
}

inline int current_cpu() { return sched_getcpu(); }

// Compiler barrier: forces the compiler to assume memory pointed to by `p`
// was read/modified, so stores before it cannot be eliminated.
inline void clobber(const void* p) { asm volatile("" : : "r"(p) : "memory"); }

// Busy-wait for `ms` milliseconds so the core leaves idle/low-frequency
// states before a short timed region (no system settings are changed).
inline void spin_warmup(int ms) {
    const auto end = std::chrono::steady_clock::now() + std::chrono::milliseconds(ms);
    volatile std::uint64_t sink = 0;
    while (std::chrono::steady_clock::now() < end) sink = sink + 1;
}

inline std::uint64_t xorshift64(std::uint64_t& s) {
    s ^= s << 13;
    s ^= s >> 7;
    s ^= s << 17;
    return s;
}

}  // namespace bench
