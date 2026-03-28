# Benchmarking Functions with stx.benchmark

The benchmarking sub-system measures how long functions take to run, with warmup runs and statistical summaries.

## benchmark_function

```python
from scitex.benchmark import benchmark_function, BenchmarkResult

import numpy as np

def my_fft(x):
    return np.fft.fft(x)

data = np.random.randn(8192)

result = benchmark_function(
    func=my_fft,
    args=(data,),
    iterations=50,   # number of timed runs (default: 10)
    warmup=2,        # warmup runs before timing (default: 2)
    input_size="8192 samples",
    measure_memory=True,  # requires psutil
)

print(result)
# my_fft: 0.000123s +- 0.000005s (n=50)

print(result.mean_time)    # float (seconds)
print(result.std_time)     # float
print(result.min_time)     # float
print(result.max_time)     # float
print(result.memory_usage) # MB, or None if psutil not installed
```

## BenchmarkResult fields

| Field | Type | Description |
|-------|------|-------------|
| `function_name` | str | Name of the benchmarked function |
| `module` | str | Module where function is defined |
| `mean_time` | float | Mean elapsed time in seconds |
| `std_time` | float | Standard deviation of elapsed time |
| `min_time` | float | Minimum elapsed time |
| `max_time` | float | Maximum elapsed time |
| `iterations` | int | Number of timed runs |
| `input_size` | str or None | User-supplied size description |
| `memory_usage` | float or None | RSS memory in MB (requires psutil) |

## compare_implementations

Compare multiple implementations side-by-side:

```python
from scitex.benchmark import compare_implementations

def baseline_sort(arr):
    return sorted(arr)

def numpy_sort(arr):
    return np.sort(arr)

def data_gen():
    arr = list(np.random.randn(10000))
    return (arr,), {}

df = compare_implementations(
    implementations={"builtin": baseline_sort, "numpy": numpy_sort},
    test_data_generator=data_gen,
    iterations=20,
)
print(df)
# Columns: implementation, mean_time, std_time, speedup
# speedup is relative to the first implementation
```

## BenchmarkSuite

Group multiple benchmarks together and run them as a suite:

```python
from scitex.benchmark import BenchmarkSuite

suite = BenchmarkSuite("Signal Processing")

suite.add_benchmark(
    func=np.fft.fft,
    test_data_generator=lambda: ((np.random.randn(8192),), {}),
    name="FFT 8192",
    sizes=["8192"],
)

suite.add_benchmark(
    func=np.fft.fft,
    test_data_generator=lambda: ((np.random.randn(65536),), {}),
    name="FFT 65536",
    sizes=["65536"],
)

df = suite.run(iterations=20, verbose=True)
suite.save_results("fft_benchmarks.csv")

# Compare against a saved baseline
comparison = suite.compare_with_baseline("fft_baseline.csv")
print(comparison[["function", "size", "speedup"]])
```

## Pre-defined Suite Runners

```python
from scitex.benchmark import run_all_benchmarks

# Run pre-defined suites for IO and stats modules
results = run_all_benchmarks(output_dir="./benchmark_results")
# Saves: io_benchmark.csv, stats_benchmark.csv, benchmark_summary.csv
```
