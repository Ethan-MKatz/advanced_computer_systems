#include <algorithm>
#include <chrono>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <random>
#include <vector>

struct alignas(64) Node {
    std::uint32_t next;
    char padding[60];
};

static_assert(sizeof(Node) == 64, "Each node must occupy 64 bytes.");

int main(int argc, char** argv) {
    if (argc != 3) {
        std::cerr << "Usage: " << argv[0]
                  << " <working_set_KiB> <accesses_in_millions>\n";
        return 1;
    }

    const std::size_t kib = std::stoull(argv[1]);
    const std::uint64_t millions = std::stoull(argv[2]);

    if (kib == 0 || millions == 0 ||
        kib * 1024 % sizeof(Node) != 0) {
        std::cerr << "Invalid working-set size or access count.\n";
        return 1;
    }

    const std::size_t node_count = kib * 1024 / sizeof(Node);

    if (node_count < 2) {
        std::cerr << "Working set must contain at least two nodes.\n";
        return 1;
    }

    std::vector<Node> nodes(node_count);
    std::vector<std::size_t> order(node_count);
    std::iota(order.begin(), order.end(), 0);

    std::mt19937 rng(12345);
    std::shuffle(order.begin(), order.end(), rng);

    // Construct one randomized cycle through every cache-line-sized node.
    for (std::size_t i = 0; i < node_count; ++i) {
        nodes[order[i]].next = static_cast<std::uint32_t>(
            order[(i + 1) % node_count]);
    }

    std::uint32_t index = 0;

    // Warm-up.
    for (std::size_t i = 0; i < node_count * 2; ++i) {
        index = nodes[index].next;
    }

    const std::uint64_t accesses = millions * 1'000'000ULL;

    const auto start = std::chrono::steady_clock::now();

    for (std::uint64_t i = 0; i < accesses; ++i) {
        index = nodes[index].next;
    }

    const auto stop = std::chrono::steady_clock::now();

    const double seconds =
        std::chrono::duration<double>(stop - start).count();

    const double ns_per_access = seconds * 1e9 / accesses;

    std::cout << kib << ','
              << accesses << ','
              << std::fixed << std::setprecision(3)
              << ns_per_access << ','
              << index << '\n';
}
