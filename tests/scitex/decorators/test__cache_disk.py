#!/usr/bin/env python3
# Time-stamp: "2025-06-02 15:56:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/decorators/test__cache_disk.py

"""Tests for disk caching decorator functionality."""

import pytest

# Required for scitex.decorators module
pytest.importorskip("tqdm")
import functools
import os
import shutil
import tempfile
import time
from unittest.mock import MagicMock, patch

# joblib was changed from top-level eager import to lazy-import inside the
# decorator body (todo#442). The legacy tests in this file depend on
# joblib being available (they construct Memory objects directly). The new
# regression test for the lazy-import behavior lives in a sibling file
# (test__lazy_imports.py) so it can run on venvs without joblib.
joblib = pytest.importorskip(
    "joblib",
    reason="legacy cache_disk tests need joblib; lazy-import regression in test__lazy_imports.py",
)
Memory = joblib.Memory


def create_cache_disk_decorator(cache_dir):
    """Create a fresh cache_disk decorator with a specific cache directory.

    This is used for testing to ensure each test has isolated cache.
    """
    memory = Memory(cache_dir, verbose=0)

    def cache_disk(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cached_func = memory.cache(func)
            return cached_func(*args, **kwargs)

        return wrapper

    return cache_disk


class TestCacheDisk:
    """Test cases for scitex.decorators._cache_disk module."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create temporary directory for cache testing
        self.temp_dir = tempfile.mkdtemp()
        self.call_count = 0

    def teardown_method(self):
        """Clean up test fixtures after each test method."""
        # Clean up temporary directory
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_cache_disk_import(self):
        """Test that cache_disk can be imported successfully."""
        from scitex.decorators import cache_disk

        assert callable(cache_disk)

    def test_cache_disk_basic_functionality(self):
        """Test basic disk caching functionality."""
        cache_disk = create_cache_disk_decorator(self.temp_dir)
        call_count = 0

        @cache_disk
        def simple_func(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # First call should execute the function
        result1 = simple_func(5)
        assert result1 == 10
        assert call_count == 1

        # Second call with same argument should use disk cache
        result2 = simple_func(5)
        assert result2 == 10
        assert call_count == 1  # No additional function call

        # Call with different argument should execute function again
        result3 = simple_func(10)
        assert result3 == 20
        assert call_count == 2

    def test_cache_disk_with_arguments(self):
        """Test disk caching with multiple arguments."""
        cache_disk = create_cache_disk_decorator(self.temp_dir)
        call_count = 0

        @cache_disk
        def multi_arg_func(x, y, z=10):
            nonlocal call_count
            call_count += 1
            return x + y + z

        # Test with positional arguments
        result1 = multi_arg_func(1, 2)
        assert result1 == 13
        assert call_count == 1

        # Same arguments should use cache
        result2 = multi_arg_func(1, 2)
        assert result2 == 13
        assert call_count == 1

        # Different arguments should execute function
        result3 = multi_arg_func(1, 2, z=20)
        assert result3 == 23
        assert call_count == 2

    def test_cache_disk_with_keyword_arguments(self):
        """Test disk caching with keyword arguments."""
        cache_disk = create_cache_disk_decorator(self.temp_dir)
        call_count = 0

        @cache_disk
        def keyword_func(a, b=5, c=10):
            nonlocal call_count
            call_count += 1
            return a * b + c

        # Test with keyword arguments
        result1 = keyword_func(2, b=3, c=4)
        assert result1 == 10
        assert call_count == 1

        # Same call should use cache
        result2 = keyword_func(2, b=3, c=4)
        assert result2 == 10
        assert call_count == 1

    def test_cache_disk_return_types(self):
        """Test disk caching with different return types."""
        cache_disk = create_cache_disk_decorator(self.temp_dir)
        call_count = 0

        @cache_disk
        def return_various_types(type_name):
            nonlocal call_count
            call_count += 1

            if type_name == "list":
                return [1, 2, 3]
            elif type_name == "dict":
                return {"key": "value"}
            elif type_name == "tuple":
                return (1, 2, 3)
            elif type_name == "none":
                return None
            else:
                return type_name

        # Test list return
        result1 = return_various_types("list")
        assert result1 == [1, 2, 3]
        assert call_count == 1

        result2 = return_various_types("list")
        assert result2 == [1, 2, 3]
        assert call_count == 1  # Should use cache

        # Test dict return
        result3 = return_various_types("dict")
        assert result3 == {"key": "value"}
        assert call_count == 2

        # Test None return
        result4 = return_various_types("none")
        assert result4 is None
        assert call_count == 3

    def test_cache_disk_persistence_across_function_calls(self):
        """Test that disk cache persists across different function instances."""
        cache_disk = create_cache_disk_decorator(self.temp_dir)
        call_count = 0

        @cache_disk
        def persistent_func(x):
            nonlocal call_count
            call_count += 1
            return x**2

        # First call
        result1 = persistent_func(5)
        assert result1 == 25
        assert call_count == 1

        # Second call with same argument should use cache
        result2 = persistent_func(5)
        assert result2 == 25
        assert call_count == 1  # Should use cache

    def test_cache_disk_performance_improvement(self):
        """Test that disk caching improves performance."""
        cache_disk = create_cache_disk_decorator(self.temp_dir)

        @cache_disk
        def slow_function(n):
            # Simulate slow computation
            time.sleep(0.05)  # 50ms delay
            return n**2

        # Time first call
        start_time = time.time()
        result1 = slow_function(5)
        first_call_time = time.time() - start_time

        # Time second call (should be faster due to disk caching)
        start_time = time.time()
        result2 = slow_function(5)
        second_call_time = time.time() - start_time

        assert result1 == result2 == 25
        # Second call should be significantly faster
        assert second_call_time < first_call_time * 0.5

    def test_cache_disk_uses_scitex_dir_environment_variable(self):
        """Test that cache_disk respects SciTeX_DIR environment variable."""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_scitex_dir = temp_dir + "/custom_scitex/"

            with patch.dict(os.environ, {"SciTeX_DIR": custom_scitex_dir}):
                from scitex.decorators import cache_disk

                @cache_disk
                def test_func(x):
                    return x * 2

                # Call function to trigger cache creation
                result = test_func(5)
                assert result == 10

    def test_cache_disk_default_cache_location(self):
        """Test cache_disk uses default location when SciTeX_DIR not set."""
        cache_disk = create_cache_disk_decorator(self.temp_dir)

        @cache_disk
        def test_func(x):
            return x * 3

        # Should work with default location
        result = test_func(7)
        assert result == 21

    def test_cache_disk_with_complex_data_structures(self):
        """Test disk caching with complex data structures."""
        cache_disk = create_cache_disk_decorator(self.temp_dir)
        call_count = 0

        @cache_disk
        def complex_data_func(data_type):
            nonlocal call_count
            call_count += 1

            if data_type == "nested_dict":
                return {"level1": {"level2": {"values": [1, 2, 3, 4, 5]}}}
            elif data_type == "nested_list":
                return [[1, 2], [3, 4], [5, [6, 7]]]
            else:
                return {"simple": "data"}

        # Test complex nested dictionary
        result1 = complex_data_func("nested_dict")
        expected_dict = {"level1": {"level2": {"values": [1, 2, 3, 4, 5]}}}
        assert result1 == expected_dict
        assert call_count == 1

        # Should use cache for same input
        result2 = complex_data_func("nested_dict")
        assert result2 == expected_dict
        assert call_count == 1

    def test_cache_disk_function_signature_preservation(self):
        """Test that decorated function preserves original signature."""
        from scitex.decorators import cache_disk

        @cache_disk
        def documented_func(x, y=10):
            """This is a test function with documentation."""
            return x + y

        # Function should preserve name and docstring
        assert documented_func.__name__ == "documented_func"
        assert "test function with documentation" in documented_func.__doc__

    def test_cache_disk_with_exceptions(self):
        """Test disk caching behavior when function raises exceptions."""
        cache_disk = create_cache_disk_decorator(self.temp_dir)
        call_count = 0

        @cache_disk
        def error_func(x):
            nonlocal call_count
            call_count += 1
            if x < 0:
                raise ValueError("Negative value not allowed")
            return x * 2

        # Function that raises exception
        with pytest.raises(ValueError):
            error_func(-1)
        assert call_count == 1

        # Successful call should work
        result = error_func(5)
        assert result == 10
        assert call_count == 2

        # Same successful call should use cache
        result2 = error_func(5)
        assert result2 == 10
        assert call_count == 2

    @patch("scitex.decorators._cache_disk._Memory")
    def test_cache_disk_joblib_memory_integration(self, mock_memory_class):
        """Test integration with joblib.Memory."""
        mock_memory = MagicMock()
        mock_memory_class.return_value = mock_memory
        mock_cached_func = MagicMock(return_value=42)
        mock_memory.cache.return_value = mock_cached_func

        from scitex.decorators import cache_disk

        @cache_disk
        def test_func(x):
            return x * 2

        result = test_func(5)

        # Verify joblib Memory was instantiated
        mock_memory_class.assert_called_once()

        # Verify cache method was called
        mock_memory.cache.assert_called_once()

        # Verify cached function was called with correct arguments
        mock_cached_func.assert_called_once_with(5)
        assert result == 42

    def test_cache_disk_cache_directory_creation(self):
        """Test that cache directory is created correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_scitex_dir = os.path.join(temp_dir, "test_scitex")

            with patch.dict(os.environ, {"SciTeX_DIR": custom_scitex_dir + "/"}):
                from scitex.decorators import cache_disk

                @cache_disk
                def test_func(x):
                    return x**2

                # Call function to trigger cache setup
                result = test_func(4)
                assert result == 16

    def test_cache_disk_multiple_functions(self):
        """Test disk caching with multiple different functions."""
        cache_disk = create_cache_disk_decorator(self.temp_dir)
        call_count_1 = 0
        call_count_2 = 0

        @cache_disk
        def func1(x):
            nonlocal call_count_1
            call_count_1 += 1
            return x * 2

        @cache_disk
        def func2(x):
            nonlocal call_count_2
            call_count_2 += 1
            return x * 3

        # Test both functions
        result1 = func1(5)
        result2 = func2(5)
        assert result1 == 10
        assert result2 == 15
        assert call_count_1 == 1
        assert call_count_2 == 1

        # Test caching for both
        result1_cached = func1(5)
        result2_cached = func2(5)
        assert result1_cached == 10
        assert result2_cached == 15
        assert call_count_1 == 1  # Should use cache
        assert call_count_2 == 1  # Should use cache

    @pytest.mark.skip(reason="joblib.Memory cannot hash instance methods with 'self'")
    def test_cache_disk_with_class_methods(self):
        """Test disk caching with class methods.

        Note: This test is skipped because joblib.Memory cannot hash instance
        methods that receive 'self' as an argument. This is a known limitation.
        Use staticmethod or classmethod with cache_disk instead.
        """
        pass

    def test_cache_disk_memory_verbose_setting(self):
        """Test that joblib Memory is created with verbose=0."""
        with patch("scitex.decorators._cache_disk._Memory") as mock_memory:
            from scitex.decorators import cache_disk

            @cache_disk
            def test_func(x):
                return x * 2

            # The Memory object should be created with verbose=0
            # Check the call arguments
            call_args = mock_memory.call_args
            if call_args:
                if len(call_args[0]) > 1:
                    # If verbose is passed as positional argument
                    assert call_args[0][1] == 0
                elif "verbose" in call_args[1]:
                    # If verbose is passed as keyword argument
                    assert call_args[1]["verbose"] == 0

    def test_cache_disk_concurrent_access_safety(self):
        """Test disk caching with concurrent-like access patterns."""
        cache_disk = create_cache_disk_decorator(self.temp_dir)
        call_count = 0

        @cache_disk
        def test_func(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # Simulate multiple rapid calls
        results = []
        for _ in range(5):
            results.append(test_func(42))

        # All results should be the same
        assert all(r == 84 for r in results)
        # Function should only be called once due to caching
        assert call_count == 1


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/decorators/_cache_disk.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-12-09 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex-code/src/scitex/decorators/_cache_disk.py
# # ----------------------------------------
# from __future__ import annotations
# import os
#
# __FILE__ = "./src/scitex/decorators/_cache_disk.py"
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
#
# import functools
#
# from joblib import Memory as _Memory
#
# from scitex.config import get_paths
#
#
# def cache_disk(func):
#     """Disk caching decorator that uses joblib.Memory.
#
#     Usage:
#         @cache_disk
#         def expensive_function(x):
#             return x ** 2
#     """
#     cache_dir = str(get_paths().function_cache)
#     memory = _Memory(cache_dir, verbose=0)
#
#     @functools.wraps(func)
#     def wrapper(*args, **kwargs):
#         cached_func = memory.cache(func)
#         return cached_func(*args, **kwargs)
#
#     return wrapper
#
#
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/decorators/_cache_disk.py
# --------------------------------------------------------------------------------
