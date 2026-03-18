<!-- ---
!-- Timestamp: 2025-08-31 05:10:07
!-- Author: ywatanabe
!-- File: /home/ywatanabe/.claude/to_claude/guidelines/python/NOT-FULL-PYTEST-BUT-PARTIAL-PYTEST.md
!-- --- -->

## Do not run `pytest tests/`
Running pytest for all tests takes quite long time (like more than 10 min) and need multiple CPU cores to run. So, in this project, `running full-test` is responsible for the user. Specifically, the user runs the following command regularly so that please check the `test-full-log-latest.txt` with carefully checking the timestamp

``` bash
LOG_FILE=test-full-log-"$(date +%Y-%m-%d-%H:%M:%S)".txt
make test-full | tee "$LOG_FILE" 2>&1
ln -sfr "$LOG_FILE" test-full-log-latest.txt
tail -n 1 "$LOG_FILE"
# ==== 154 failed, 1712 passed, 27 skipped, 43 warnings in 391.44s (0:06:31) =====make: *** [Makefile:76: test-full] Error 1
```

## Run pytest partically: `pytest tests/specific/directory
However, you may want to check pytest soon after your edition. In that case, please run pytest for only specific, minimal tests to minimize time used.

<!-- EOF -->
