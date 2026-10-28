// Experiment 7 (timing-only): page locality and page size.
//
// A dependent pointer chase visits `pages * lines_per_page` cache lines in a
// random cyclic order. The lines live in `pages` consecutive 4 KiB page slots
// of a buffer, `lines_per_page` lines per slot at random distinct offsets
// within the slot. Holding the line count fixed while spreading the lines over
// more pages keeps the data footprint constant (e.g. 8192 lines = 512 KiB)
// but grows the number of distinct 4 KiB pages, i.e. the translation reach
// needed. Comparing regular 4 KiB pages with transparent huge pages (2 MiB,
// requested via madvise) isolates the page-size effect.
//
// TLB-miss counters are NOT available (perf_event_open -> EACCES); measured
// values are time per access, minor page faults during setup (getrusage) and
// AnonHugePages backing (/proc/self/smaps_rollup).
//
// Output (CSV, no header): pages,lines_per_page,lines,span_KiB,thp,accesses,
//   seconds,ns_per_access,setup_minor_faults,anon_huge_KiB,checksum,cpu_start,cpu_end
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <random>
#include <string>
#include <vector>

#include "common.hpp"

int main(int argc, char** argv) {
    if (argc != 6) {
        std::cerr << "Usage: " << argv[0]
                  << " <pages> <lines_per_page 1-64> <thp 0|1> <accesses_millions> <seed>\n";
        return 1;
    }
    const std::size_t pages = std::stoull(argv[1]);
    const std::size_t lpp = std::stoull(argv[2]);
    const bool thp = std::stoi(argv[3]) != 0;
    const std::uint64_t accesses = std::stoull(argv[4]) * 1'000'000ULL;
    const unsigned seed = static_cast<unsigned>(std::stoul(argv[5]));
    if (pages == 0 || lpp == 0 || lpp > 64) {
        std::cerr << "Invalid arguments.\n";
        return 1;
    }
    constexpr std::size_t kPage = 4096, kLine = 64;
    const std::size_t span = pages * kPage;
    const std::size_t lines = pages * lpp;

    const long faults0 = bench::minor_faults();
    auto* buf = static_cast<std::uint64_t*>(bench::alloc_buffer(span, thp));
    const long setup_faults = bench::minor_faults() - faults0;
    const long huge_kib = bench::anon_huge_kib();

    // Choose lpp distinct line slots in every page, then link all chosen lines
    // into one random cycle. Each line stores the word index of its successor.
    std::mt19937_64 rng(seed);
    std::vector<std::uint64_t> words;
    words.reserve(lines);
    std::vector<std::size_t> slots(kPage / kLine);
    for (std::size_t p = 0; p < pages; ++p) {
        std::iota(slots.begin(), slots.end(), 0);
        std::shuffle(slots.begin(), slots.end(), rng);
        for (std::size_t j = 0; j < lpp; ++j)
            words.push_back((p * kPage + slots[j] * kLine) / 8);
    }
    std::shuffle(words.begin(), words.end(), rng);
    for (std::size_t i = 0; i < lines; ++i) buf[words[i]] = words[(i + 1) % lines];

    std::uint64_t idx = words[0];
    for (std::size_t i = 0; i < 2 * lines; ++i) idx = buf[idx];  // warm-up

    const int cpu_start = bench::current_cpu();
    const auto t0 = std::chrono::steady_clock::now();
    for (std::uint64_t i = 0; i < accesses; ++i) idx = buf[idx];
    const double s = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();

    std::cout << pages << ',' << lpp << ',' << lines << ',' << span / 1024 << ',' << thp << ','
              << accesses << ',' << std::fixed << std::setprecision(6) << s << ','
              << std::setprecision(4) << s * 1e9 / accesses << ',' << setup_faults << ','
              << huge_kib << ',' << idx << ',' << cpu_start << ',' << bench::current_cpu() << '\n';
    std::free(buf);
    return 0;
}
