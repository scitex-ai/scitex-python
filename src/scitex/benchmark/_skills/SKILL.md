---
name: stx.benchmark
description: Performance benchmarking, profiling, and monitoring tools for SciTeX functions.
---

# stx.benchmark

The `stx.benchmark` module provides tools for measuring, profiling, and monitoring the performance of SciTeX functions. It supports function-level benchmarking, module-level profiling, and continuous performance monitoring.

## Python API

```python
import scitex as stx

# Benchmark a single function
result = stx.benchmark.benchmark_function(my_func, args=(data,), n_runs=100)
print(result.mean_time, result.std_time)

# Benchmark an entire module
suite = stx.benchmark.benchmark_module(stx.dsp)

# Profile a function
report = stx.benchmark.profile_function(my_func, args=(data,))
print(stx.benchmark.get_profile_report(report))

# Monitor performance continuously
monitor = stx.benchmark.PerformanceMonitor()
with stx.benchmark.track_performance("my_operation"):
    my_func()

stats = stx.benchmark.get_performance_stats()

# Compare implementations
results = stx.benchmark.compare_implementations(
    {"impl_a": func_a, "impl_b": func_b},
    args=(data,)
)
```

## Key Features

- `benchmark_function` / `benchmark_module` — timing benchmarks with statistical summaries
- `BenchmarkResult` / `BenchmarkSuite` — structured result objects
- `profile_function` / `profile_module` — cProfile-based profiling
- `PerformanceMonitor` / `track_performance` — continuous performance monitoring
- `compare_implementations` — side-by-side performance comparison
