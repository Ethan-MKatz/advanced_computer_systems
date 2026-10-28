// Experiment 4: memory-level-parallelism (concurrency) sweep.
//
// One random cyclic permutation of 64-byte nodes spans the whole buffer.
// Each thread walks K independent pointer chains that start at evenly spaced
// positions on that cycle, so chains never touch the same nodes during a run.
// Every load is dependent on the previous load of the *same* chain, so each
// chain has at most one outstanding miss; K chains therefore allow up to K
// misses in flight per thread. K is the configured concurrency (L).
//
// Measured: elapsed time for `steps` loads per chain.
//   lambda (loads/s) = threads * K * steps / elapsed
//   W (ns)           = elapsed / steps  (average time per step of one chain)
// Note L = lambda * W = threads * K holds by construction here; the useful
// quantities are how W(K) grows and where lambda stops scaling.
//
// Output (CSV, no header): ws_MiB,thp,threads,chains_per_thread,steps,
//   seconds,loads_per_s,ns_per_step,anon_huge_KiB,cpus,checksum
#include <pthread.h>

#include <algorithm>
#include <array>
#include <atomic>
#include <chrono>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <random>
#include <string>
#include <thread>
#include <vector>

#include "common.hpp"

struct alignas(64) Node {
    std::uint64_t next;
    char pad[56];
};

template <int K>
std::uint64_t walk(const Node* nodes, const std::uint64_t* starts, std::uint64_t steps) {
    std::array<std::uint64_t, K> idx;
    for (int j = 0; j < K; ++j) idx[j] = starts[j];
    for (std::uint64_t s = 0; s < steps; ++s) {
        for (int j = 0; j < K; ++j) idx[j] = nodes[idx[j]].next;
    }
    std::uint64_t sum = 0;
    for (int j = 0; j < K; ++j) sum += idx[j];
    return sum;
}

using WalkFn = std::uint64_t (*)(const Node*, const std::uint64_t*, std::uint64_t);

template <int... Ks>
WalkFn pick(int k, std::integer_sequence<int, Ks...>) {
    WalkFn fn = nullptr;
    ((k == Ks + 1 ? (fn = &walk<Ks + 1>, 0) : 0), ...);
    return fn;
}

int main(int argc, char** argv) {
    if (argc != 7) {
        std::cerr << "Usage: " << argv[0]
                  << " <ws_MiB> <chains_per_thread 1-32> <total_loads_millions>"
                     " <thp 0|1> <cpu list, e.g. 0 or 0,2> <seed>\n";
        return 1;
    }
    const std::size_t mib = std::stoull(argv[1]);
    const int k = std::stoi(argv[2]);
    const std::uint64_t total = std::stoull(argv[3]) * 1'000'000ULL;
    const bool thp = std::stoi(argv[4]) != 0;
    const std::string cpu_list = argv[5];
    const unsigned seed = static_cast<unsigned>(std::stoul(argv[6]));

    std::vector<int> cpus;
    for (std::size_t p = 0; p <= cpu_list.size();) {
        const std::size_t q = cpu_list.find(',', p);
        cpus.push_back(std::stoi(cpu_list.substr(p, q - p)));
        if (q == std::string::npos) break;
        p = q + 1;
    }
    const int threads = static_cast<int>(cpus.size());
    WalkFn fn = pick(k, std::make_integer_sequence<int, 32>{});
    if (fn == nullptr || mib == 0) {
        std::cerr << "Invalid arguments.\n";
        return 1;
    }

    const std::size_t n = mib * 1024 * 1024 / sizeof(Node);
    auto* nodes = static_cast<Node*>(bench::alloc_buffer(n * sizeof(Node), thp));
    std::vector<std::uint64_t> order(n);
    std::iota(order.begin(), order.end(), 0);
    std::mt19937_64 rng(seed);
    std::shuffle(order.begin(), order.end(), rng);
    for (std::size_t i = 0; i < n; ++i) nodes[order[i]].next = order[(i + 1) % n];

    // Chain c (over all threads) starts at cycle position c * n / (threads*K).
    const int chains = threads * k;
    std::vector<std::uint64_t> starts(chains);
    for (int c = 0; c < chains; ++c) starts[c] = order[static_cast<std::size_t>(c) * n / chains];
    const std::uint64_t steps = total / chains;
    if (steps * chains > n) {
        // Not an error, but chains would wrap into each other's segments.
        std::cerr << "warning: chains overlap (steps*chains > nodes)\n";
    }
    const long huge_kib = bench::anon_huge_kib();

    std::vector<std::uint64_t> sums(threads);
    std::atomic<int> ready{0};
    std::atomic<bool> go{false};
    std::vector<std::thread> pool;
    std::chrono::steady_clock::time_point start;
    for (int t = 0; t < threads; ++t) {
        pool.emplace_back([&, t] {
            cpu_set_t set;
            CPU_ZERO(&set);
            CPU_SET(cpus[t], &set);
            pthread_setaffinity_np(pthread_self(), sizeof(set), &set);
            // Short warm-up on this thread's chains (also faults TLB entries).
            sums[t] = fn(nodes, &starts[t * k], 1000);
            ready.fetch_add(1);
            while (!go.load(std::memory_order_acquire)) {}
            sums[t] += fn(nodes, &starts[t * k], steps);
        });
    }
    while (ready.load() != threads) {}
    start = std::chrono::steady_clock::now();
    go.store(true, std::memory_order_release);
    for (auto& th : pool) th.join();
    const auto stop = std::chrono::steady_clock::now();

    const double seconds = std::chrono::duration<double>(stop - start).count();
    std::uint64_t checksum = 0;
    for (auto s : sums) checksum += s;
    std::cout << mib << ',' << thp << ',' << threads << ',' << k << ',' << steps << ','
              << std::fixed << std::setprecision(6) << seconds << ','
              << std::setprecision(1) << chains * static_cast<double>(steps) / seconds << ','
              << std::setprecision(3) << seconds * 1e9 / steps << ',' << huge_kib << ','
              << '"' << cpu_list << '"' << ',' << checksum << '\n';
    std::free(nodes);
    return 0;
}
