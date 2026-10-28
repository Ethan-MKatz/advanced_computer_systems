// Probe whether unprivileged hardware/software counters are usable via
// perf_event_open(2). Prints one CSV row per event: name,type,status,errno_text.
#include <linux/perf_event.h>
#include <sys/syscall.h>
#include <unistd.h>

#include <cerrno>
#include <cstdint>
#include <cstring>
#include <iostream>

struct Event {
    const char* name;
    std::uint32_t type;
    std::uint64_t config;
};

static std::uint64_t cache_cfg(std::uint64_t cache, std::uint64_t op, std::uint64_t result) {
    return cache | (op << 8) | (result << 16);
}

int main() {
    const Event events[] = {
        {"hw_cpu_cycles", PERF_TYPE_HARDWARE, PERF_COUNT_HW_CPU_CYCLES},
        {"hw_cache_misses", PERF_TYPE_HARDWARE, PERF_COUNT_HW_CACHE_MISSES},
        {"l1d_read_miss", PERF_TYPE_HW_CACHE,
         cache_cfg(PERF_COUNT_HW_CACHE_L1D, PERF_COUNT_HW_CACHE_OP_READ,
                   PERF_COUNT_HW_CACHE_RESULT_MISS)},
        {"dtlb_read_miss", PERF_TYPE_HW_CACHE,
         cache_cfg(PERF_COUNT_HW_CACHE_DTLB, PERF_COUNT_HW_CACHE_OP_READ,
                   PERF_COUNT_HW_CACHE_RESULT_MISS)},
        {"sw_page_faults", PERF_TYPE_SOFTWARE, PERF_COUNT_SW_PAGE_FAULTS},
        {"sw_task_clock", PERF_TYPE_SOFTWARE, PERF_COUNT_SW_TASK_CLOCK},
    };

    std::cout << "event,type,status,detail\n";
    for (const Event& e : events) {
        perf_event_attr attr;
        std::memset(&attr, 0, sizeof(attr));
        attr.size = sizeof(attr);
        attr.type = e.type;
        attr.config = e.config;
        attr.disabled = 1;
        attr.exclude_kernel = 1;
        attr.exclude_hv = 1;

        const long fd = syscall(SYS_perf_event_open, &attr, 0, -1, -1, 0);
        if (fd < 0) {
            std::cout << e.name << ',' << e.type << ",unavailable," << std::strerror(errno) << '\n';
        } else {
            std::cout << e.name << ',' << e.type << ",available,fd_opened\n";
            close(static_cast<int>(fd));
        }
    }
    return 0;
}
