<!-- ---
!-- Timestamp: 2025-06-06 09:05:00
!-- Author: ywatanabe
!-- File: /home/ywatanabe/.claude/to_claude/guidelines/programming_common/IMPORTANT-documentation-performance-claims.md
!-- --- -->

# Performance Claims in Documentation Guidelines

## Core Principle
**NEVER include unverified performance claims in source documentation.**
Performance numbers become outdated, environment-dependent, and damage credibility when wrong.

## Documentation Hierarchy for Performance Claims

### 1. README/Source Documentation: Functionality Only
- **DO**: Describe what the code does and how to use it
- **DO**: Explain architectural decisions that enable performance
- **DON'T**: Include specific numbers (e.g., "100x faster", "0.5ms latency")
- **DON'T**: Make comparative claims without current verification

**Good Example:**
```markdown
## Performance
Designed for GPU acceleration with vectorized operations processing
all operations simultaneously. See `examples/benchmarks/` for
performance comparisons in your environment.
```

**Bad Example:**
```markdown
## Performance
| Implementation | Time (ms) | Speedup |
|---------------|-----------|---------|
| Legacy        | 1000      | 1.0x    |
| Our Solution  | 10        | 100x    |
```

### 2. Examples/Benchmarks: Measurement Scripts
- **DO**: Provide runnable comparison scripts
- **DO**: Show users how to measure performance
- **DO**: Include comparison with reference implementations
- **DO**: Document measurement methodology

**Structure:**
```
examples/
├── benchmarks/
│   ├── performance_comparison.py
│   ├── memory_usage_analysis.py
│   └── README.md  # Explains how to run and interpret
```

### 3. Tests: Correctness & Regression Only
- **DO**: Test accuracy against reference implementations
- **DO**: Include basic regression tests (relative performance)
- **DON'T**: Test absolute performance numbers
- **DON'T**: Fail tests based on environment-dependent timing

## Language-Specific Guidelines

### Python
```python
# Good: Architecture description
class VectorizedProcessor:
    """
    Processes all items simultaneously using vectorized operations
    for improved performance over sequential processing.
    """

# Bad: Specific claims
class VectorizedProcessor:
    """
    100x faster than sequential processing (measured on RTX 4090).
    """
```

### Documentation Comments
```python
def optimized_algorithm(data):
    """
    Optimized implementation using parallel processing.

    See examples/benchmarks/algorithm_comparison.py for
    performance analysis against standard implementations.
    """
```

## When Performance Claims Are Acceptable

### 1. Big-O Complexity
```markdown
## Complexity
- Time: O(n log n) vs O(n²) for naive implementation
- Space: O(1) additional memory
```

### 2. Algorithmic Improvements
```markdown
## Algorithm
Uses XYZ algorithm which provides theoretical speedup over
ABC algorithm for large datasets. See [paper reference].
```

### 3. Qualified Statements
```markdown
## Design Goals
Designed to minimize memory allocations and leverage GPU
parallelization for compute-intensive workloads.
```

## Migration Strategy for Existing Claims

### Step 1: Audit Current Documentation
```bash
# Find performance claims
grep -r -i "faster\|speedup\|performance\|benchmark" docs/ README.md
```

### Step 2: Move Numbers to Examples
1. Create `examples/benchmarks/` directory
2. Move specific claims to runnable scripts
3. Update documentation to reference examples

### Step 3: Rewrite Claims
- "100x faster" → "designed for high performance"
- "0.5ms latency" → "optimized for low latency"
- "Uses 50% less memory" → "memory-efficient implementation"

## Anti-Patterns to Avoid

### ❌ Outdated Benchmarks
```markdown
# Benchmarked on Python 3.6, NumPy 1.14 (2018)
```

### ❌ Hardware-Specific Claims
```markdown
# 50x speedup on RTX 4090 with CUDA 11.8
```

### ❌ Version-Specific Numbers
```markdown
# 20% faster than v1.2.3
```

### ❌ Unqualified Comparisons
```markdown
# Fastest JSON parser available
```

## Benefits of This Approach

1. **Credibility**: Documentation stays accurate over time
2. **Flexibility**: Users measure in their specific environment
3. **Education**: Examples teach users how to benchmark
4. **Maintenance**: No need to update numbers constantly
5. **Honesty**: Clear about what's verified vs claimed

## Your Understanding Check
Did you understand the guideline? If yes, please say:
`CLAUDE UNDERSTOOD: <THIS FILE PATH HERE>`

<!-- EOF -->
