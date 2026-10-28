# Project 3 — SSD Performance Profiling: Methodology

This file documents how the data was collected. It does not contain results or analysis.

## 1. Environment (verified 2026-10-26, not assumed)

| Item | Value | Source |
|---|---|---|
| Machine | Lenovo ThinkPad X1 Carbon Gen 13 | user |
| SSD | Samsung `MZVLC1T0HFLU-00BLL` (PM9C1a family, 1 TB, 953.9 GiB), firmware `3L2QNXH7`, PCI ID 144d:a810 | `/sys/block/nvme0n1/device/{model,firmware_rev}`, `lspci` |
| Interface | NVMe over PCIe; negotiated link 16.0 GT/s x4 (PCIe 4.0 x4, ~7.9 GB/s raw per direction); sysfs `max_link_speed` reports 32.0 GT/s | `/sys/class/nvme/nvme0/device/current_link_{speed,width}` |
| NVMe queues | 15 I/O queues (`queue_count`), sqsize 1023, block-layer `nr_requests` 1023, scheduler `none`, logical/physical block 512 B, volatile write cache: write back | sysfs |
| NVMe power | APST enabled (`nvme_core.default_ps_max_latency_us=100000`) | sysfs (unchanged) |
| Partition / FS | `/dev/nvme0n1p3`, ext4, mounted at `/` (`rw,relatime`), 925 GB; 4 KiB fs block | `findmnt`, `stat -f` |
| Free space | 487 GB before test file; 483 GB after creating it | `df` |
| OS / kernel | Ubuntu 24.04.4 LTS, Linux 6.17.0-1033-oem (PREEMPT_DYNAMIC) | `uname`, `lsb_release` |
| CPU | Intel Core Ultra 7 255U (12 cores / 14 threads); benchmark process affinity mask `0x300f` = 6 logical CPUs | `lscpu`, `taskset -p` |
| CPU power | governor `powersave`, EPP `balance_performance`, platform profile `balanced` (left at defaults) | sysfs |
| RAM | 30 GiB (≈13 GiB available during tests), 8 GiB swap | `free -h` |
| Power source | Battery (75 %) during file preparation; on AC for the benchmark runs. AC state and battery % are logged per run in `*.meta.json` | `/sys/class/power_supply` |
| Temperature | NVMe composite sensor via hwmon (`nvme` driver), read without root, sampled at 1 Hz during every run | `/sys/class/hwmon/hwmon*/temp1_input` |
| Not available | `nvme-cli` and `smartctl` are not installed; SMART logs need root, so none were read. No `sudo` was used. | |
| fio | 3.36 (`/usr/bin/fio`), ioengine `io_uring` (psync for experiment 7) | `fio --version` |
| Python | 3.12.3 venv (`../.venv`): pandas 3.1.0, numpy 2.5.4, matplotlib 3.11.2 | |

## 2. Safety precautions and the target file

- **Only target:** the regular file `ssd/testfile/fio_testfile.bin` (4 GiB = 4 294 967 296 B) on the
  ext4 root filesystem. No raw device, partition, or mounted block device was ever given to fio.
  No `blkdiscard`, `nvme format`, `dd`, mkfs, partitioning, `sudo`, or kernel/governor changes.
- The file is created once by `scripts/prepare_testfile.py`, the only job that sets `allow_file_create=1`.
  It writes the whole file sequentially with 1 MiB direct I/O and incompressible data. This
  makes sure every block is mapped and written, so later reads go to flash rather than
  to ext4 unwritten extents (which return zeros without touching the device).
- Every benchmark job file sets `filename=${TESTFILE}`, `allow_file_create=0`, `unlink=0`.
  `scripts/fio_runner.py` refuses to run a job file that lacks these or mentions `/dev/`.
- Before **every** run the runner checks that:
  - the path is not a symlink, is a regular file, its realpath matches, and its size is exactly 4 GiB;
  - its filesystem is ext4 on `/dev/nvme0n1p3`;
  - at least 20 GiB is free;
  - the battery is above 20 % when not on AC;
  - the NVMe temperature is at most 60 °C (otherwise it waits).
- During every run, the NVMe temperature is sampled at 1 Hz. fio is interrupted if the drive
  reaches 75 °C (its warning threshold is 82.8 °C).
- Runs execute strictly one at a time. `.gitignore` in `ssd/` excludes `testfile/`.
- The test file is kept until you approve deleting it.

## 3. Common fio settings

| Setting | Value | Why |
|---|---|---|
| `direct` | 1 (except the buffered arm of exp 7) | bypass the page cache |
| `ioengine` | `io_uring` (exp 1–6), `psync` (exp 7) | async engine needed for QD>1 |
| `time_based`, `ramp_time` | runtime per experiment below; 2 s ramp (0 s for exp 6b and cold-cache exp 7) | exclude start-up transients |
| random offsets | `randseed = 4320 + trial`, `tausworthe64`, `norandommap=1`; alignment = block size (fio default `blockalign=bs`) | reproducible, aligned, independent trials |
| data pattern | `refill_buffers=0`: one fio-generated pseudo-random (incompressible) buffer per job, with fio's default `scramble_buffers`. Held constant across all write tests | |
| latency | `lat_percentiles=1`: **total latency** (submission + completion), percentiles 1…99.99 | |
| `group_reporting` | 1. Only matters for exp 4's `numjobs=4` curve, where the 4 jobs are intentionally summed into one result | |
| range | `offset=0`, `size=${SIZE}` (4 GiB unless varied) | |
| trials | 3 per configuration (2 for exp 6b). Trials are the outer loop, so slow drift affects all configurations equally | |

## 4. Workload matrix

| Exp | Job file | Varied | Fixed | Runtime | Runs |
|---|---|---|---|---|---|
| 1 QD=1 baselines | `exp1_qd1_baseline.fio` | {4 KiB randread, 4 KiB randwrite, 128 KiB seq read, 128 KiB seq write} | QD1, 1 job | 30 s | 4 × 3 |
| 2 Block size | `exp2_block_size.fio` | bs ∈ {4,16,32,64,128,256} KiB × {randread, read} × QD ∈ {1, 32} | 100 % read, 1 job | 15 s | 24 × 3 |
| 3 R/W mix | `exp3_rw_mix.fio` | rwmixread ∈ {100, 70, 50, 0} | 4 KiB randrw, QD32, 1 job | 30 s | 4 × 3 |
| 4 QD sweep | `exp4_queue_depth.fio` | numjobs=1: iodepth 1…256 (powers of 2); numjobs=4: iodepth 1…64 | 4 KiB randread | 20 s | 16 × 3 |
| 5 Tail latency | `exp5_tail_latency.fio` | iodepth = mid, knee (selected from exp 4 by `select_tail_depths.py`) | 4 KiB randread, 1 job, `json+` output | 60 s | 2 × 3 |
| 6a Working set | `exp6_working_set.fio` | range ∈ {64 MiB, 256 MiB, 1 GiB, 4 GiB} × {randread, randwrite} | 4 KiB, QD32 | 20 s | 8 × 3 |
| 6b Burst vs later | `exp6_sustained.fio` | time within run (1 s averaged logs) | 4 KiB randwrite, QD32, 4 GiB, 120 s idle before each trial | 90 s | 2 |
| 7 Pitfall | `exp7_buffered_vs_direct.fio` | direct vs buffered (cold / warm cache); plus psync with iodepth=32 (wrong effective QD) | 4 KiB random, psync, 1 GiB range | 15 s | 7 × 3 (incl. warm-up) |

**Knee rule (exp 4 → 5):** the knee is the smallest iodepth whose median IOPS reaches 90 % or more of the
numjobs=1 curve's maximum. The mid depth is knee/4 (at least 2). The chosen values are written to
`results/processed/exp5_selected_depths.json`.

**Achieved depth:** recorded two ways. (1) fio's `iodepth_level` histogram (coarse buckets).
(2) Little's Law, L = IOPS × mean total latency, computed in software. The configured depth is
the job parameter.

**Bounded writes:** the longest write test is 90 s of 4 KiB random writes per exp 6b trial. This is not
full-drive steady-state preconditioning: the drive is mostly empty, and only the 4 GiB file is overwritten.
Any burst-vs-later difference is a device-state *observation*, not a steady-state measurement.

## 5. Data products

- `results/raw/<experiment>/<run>_t<trial>.json`: fio JSON (`json+` for exp 5).
- `results/raw/<experiment>/<run>_t<trial>.meta.json`: parameters, job-file text and SHA-256, command line,
  return code, timestamps, temperature before/after/max plus the 1 Hz trace, free space before/after, power state.
- `results/raw/<experiment>/<run>_t<trial>.stderr.txt`: fio stderr.
- `results/raw/exp6_device_state/exp6b_*_{bw,iops,lat,clat,slat}.1.log`: 1 s averaged fio logs.
- `results/raw/run_log.txt`: console log of the whole campaign.
- `results/processed/all_runs.csv`: one row per run × direction. Failed runs are kept with `valid=False`.
- `results/processed/summary_by_config.csv`: median, min, max and std across trials.
- `results/processed/exp5_latency_bins.csv`, `exp6b_timeseries.csv`, `exp6b_temperature.csv`.
- `results/processed/validation_report.txt`: expected vs found run counts and a percentile monotonicity check.
- `results/plots/MANIFEST.md`: maps each plot to its data, config and script.

Units: latency in µs (fio reports ns; divided by 1000), bandwidth in MB/s = 10⁶ B/s, IOPS as reported by fio.

## 6. Reproduction

```bash
cd ssd/scripts
../../.venv/bin/python prepare_testfile.py      # once; refuses to overwrite
./run_all.sh                                    # all experiments (~80 min), parse, plot
# or step by step:
../../.venv/bin/python run_exp1_qd1.py          # ... run_exp7_pitfall.py
../../.venv/bin/python parse_results.py
../../.venv/bin/python select_tail_depths.py    # before run_exp5_tail.py
../../.venv/bin/python plot_all.py
```

Completed runs are skipped on re-run. Pass `force=True` to `run_fio` to repeat one.
To remove the test file after you have approved it: `rm ssd/testfile/fio_testfile.bin`.
