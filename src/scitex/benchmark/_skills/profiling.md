# Profiling with stx.benchmark

The profiling sub-system uses Python's `cProfile` to identify where time is spent inside a function's call stack.

## profile_function (decorator)

```python
from scitex.benchmark import profile_function, get_profile_report

@profile_function
def process_data(x):
    # some expensive computation
    return np.fft.fft(x) ** 2

# Call normally — profile is accumulated in the global profiler
for _ in range(10):
    process_data(np.random.randn(8192))

# Retrieve structured report
report = get_profile_report()
# report["process_data"]["call_count"]   -> 10
# report["process_data"]["total_time"]   -> float (seconds)
# report["process_data"]["avg_time"]     -> float
# report["process_data"]["profile"]      -> cProfile text output (top 10 callers)
```

## profile_block (context manager)

Profile an arbitrary code block — prints directly to stdout:

```python
from scitex.benchmark.profiler import profile_block

with profile_block("data_loading"):
    data = np.load("large_array.npy")
    processed = np.fft.rfft(data)
# Prints: total time + top 10 cumulative call stats
```

## profile_module

Wrap all public functions in a module with profiling:

```python
from scitex.benchmark import profile_module

profiler = profile_module("scitex.dsp", pattern="*")
# Output: "Profiling N functions in scitex.dsp"
# Now run code that calls those functions...
import scitex.dsp as dsp
dsp.some_function(data)

# Get report from the returned FunctionProfiler
report = profiler.get_report()
```

## FunctionProfiler class (direct usage)

```python
from scitex.benchmark.profiler import FunctionProfiler

profiler = FunctionProfiler()

@profiler.profile
def my_func(x):
    return np.sort(x)

for _ in range(5):
    my_func(np.random.randn(10000))

profiler.print_stats("my_func", top_n=10)
# Prints: call count, total time, avg time, and cProfile top-10
```

## track_memory (context manager)

Track memory usage for a code block (requires `psutil`):

```python
from scitex.benchmark.profiler import track_memory

with track_memory("array allocation"):
    big = np.zeros((10000, 10000))
# Prints: start/end/delta RSS in MB
```

## get_memory_usage

```python
from scitex.benchmark.profiler import get_memory_usage

mb = get_memory_usage()  # current process RSS in MB, or None if psutil missing
```
