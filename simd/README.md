# SIMD Advantage Profiling

## Overview

This project investigates the performance differences between scalar and SIMD implementations of computational kernels. Experiments examine execution time, memory bandwidth, compiler vectorization, memory locality, alignment, stride, floating-point precision, and roofline analysis.

## Project Structure

- `src/` — C++ benchmark implementations.
- `scripts/` — Scripts for collecting results and generating plots.
- `results/raw/` — Raw benchmark measurements.
- `results/processed/` — Processed benchmark data.
- `results/plots/` — Figures generated from benchmark experiments.
- `results/reports/` — Text reports and experiment analysis.
- `docs/` — Environment and configuration information.
- `build/` — Build-related files.
- `report/` — Project report materials.

## Experiments

### 1. Scalar vs. SIMD Performance
Compares execution time, speedup, and effective memory bandwidth across input sizes.

### 2. Memory Locality
Investigates how working-set size affects benchmark performance relative to the CPU cache hierarchy.

### 3. Alignment, Tail Handling, and Stride
Examines the effects of memory alignment, array lengths that do not divide evenly into vector widths, and non-unit memory strides.

### 4. Floating-Point Precision
Evaluates runtime and numerical error for different floating-point implementations.

### 5. Roofline Analysis
Uses arithmetic intensity and achieved performance to investigate computational and memory-bandwidth limits.

## Building and Running

The benchmark implementations are written in C++. Compiler options and run commands depend on the specific experiment. See the source files, scripts, and environment notes for details.

## Reproducibility

Benchmark results depend on the processor, compiler, operating system, CPU frequency, background workload, and measurement procedure. Results should be interpreted in the context of the recorded experimental environment.

## Notes

This repository preserves experimental data and plots alongside the source code used to generate them. Consult the individual scripts and result files to determine the exact configuration for each experiment.
