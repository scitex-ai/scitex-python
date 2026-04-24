"""Tests for `scitex.parallel.run` — threaded map over a tuple-args list."""

from __future__ import annotations

import time

import pytest

import scitex.parallel as par

# ---------------------------------------------------------------------------
# Core ordering + correctness
# ---------------------------------------------------------------------------


def _square(x):
    return x * x


def _add(a, b):
    return a + b


class TestOrderAndCorrectness:
    def test_preserves_order(self):
        result = par.run(_square, [(1,), (2,), (3,), (4,)], n_jobs=2)
        assert result == [1, 4, 9, 16]

    def test_multi_arg_tuples(self):
        result = par.run(_add, [(1, 2), (3, 4), (10, 20)], n_jobs=2)
        assert result == [3, 7, 30]

    def test_empty_input_raises(self):
        # Contract: empty args_list is a programmer error, not a no-op.
        with pytest.raises(ValueError, match="empty"):
            par.run(_square, [], n_jobs=2)

    def test_single_job(self):
        result = par.run(_square, [(5,)], n_jobs=1)
        assert result == [25]


# ---------------------------------------------------------------------------
# n_jobs semantics
# ---------------------------------------------------------------------------


class TestNJobs:
    def test_n_jobs_negative_one(self):
        # -1 == use all processors; functionally must produce correct result
        result = par.run(_square, [(i,) for i in range(8)], n_jobs=-1)
        assert result == [i * i for i in range(8)]

    def test_n_jobs_more_than_tasks(self):
        result = par.run(_square, [(1,), (2,)], n_jobs=16)
        assert result == [1, 4]


# ---------------------------------------------------------------------------
# Parallelism actually speeds up I/O-bound work
# ---------------------------------------------------------------------------


def _sleepy(duration):
    time.sleep(duration)
    return duration


class TestSpeedup:
    def test_parallel_faster_than_sequential(self):
        # 4 tasks × 0.1 s sleep
        args = [(0.1,)] * 4

        t0 = time.time()
        seq = par.run(_sleepy, args, n_jobs=1)
        t_seq = time.time() - t0

        t0 = time.time()
        parr = par.run(_sleepy, args, n_jobs=4)
        t_par = time.time() - t0

        assert seq == parr == [0.1] * 4
        # 4-way parallel should be at least 2× faster — generous margin
        # for CI flakiness
        assert t_par < t_seq * 0.75


# ---------------------------------------------------------------------------
# Error propagation
# ---------------------------------------------------------------------------


def _boom(x):
    if x == 2:
        raise ValueError(f"boom at {x}")
    return x


class TestErrors:
    def test_exception_propagates(self):
        with pytest.raises(ValueError, match="boom at 2"):
            par.run(_boom, [(1,), (2,), (3,)], n_jobs=2)


# EOF
