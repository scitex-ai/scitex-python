<!-- ---
!-- Timestamp: 2025-08-30 06:36:14
!-- Author: ywatanabe
!-- File: /home/ywatanabe/.claude/to_claude/guidelines/python/cipdb.md
!-- --- -->

########################################
Official README.md
########################################

``` markdown
# cipdb - Conditional iPDB

Simple conditional debugging for Python with ID-based breakpoint control.

[![PyPI version](https://badge.fury.io/py/cipdb.svg)](https://badge.fury.io/py/cipdb)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install cipdb
```

## Quick Start

### Control by Global State Call in Python

```python
# Disable all debugging programmatically
cipdb.disable()
```

### Controll by Environmental Variable

``` python
CIPDB_ID=false python your_script.py
```

### Control by Boolean

```python
import cipdb

cipdb.set_trace()       # Identical with ipdb.set_trace()
cipdb.set_trace(False)  # Identical with pass
cipdb.set_trace(os.getenv("DEBUG")) # Development vs Production
cipdb.set_trace(os.getenv("AGENT_ID")=="DebuggingAgent_01") # Runner Specific for debugging by multiple agent
```

### Control by Breakpoint IDs
``` python
# your_script.py
def process_user(user):
    cipdb.set_trace(id="validate")
    validate(user)

    cipdb.set_trace(id="save")
    save_user(user)

    cipdb.set_trace(id="notify")
    send_notification(user)
```

``` bash
# Development mode: All ID breakpoints work (no env vars needed)
python your_script.py                            # All ID breakpoints trigger

# Production mode: Control with environment variables
CIPDB_IDS=validate,save python your_script.py   # Only stops at validate and save
CIPDB_IDS=save python your_script.py            # Only stops at save
CIPDB_ID=save python your_script.py             # Only stops at save (Equivalent to CIPDB_IDS=save)
```

## Priority Logic

Global Control > `CIPDB=false` Environmental Variable > ID Matching > Boolean Conditioning

## License

MIT
```


########################################
Official Example.py
########################################

``` python
#!/usr/bin/env python3
'''Examples demonstrating cipdb usage.'''

import os
import cipdb


def example_simple():
    '''Basic debugging.'''
    print("Example: Simple debugging")
    x = 10

    # Always debug
    # cipdb.set_trace()

    # Never debug
    cipdb.set_trace(False)

    print(f"x = {x}")


def example_id_based():
    '''ID-based breakpoint debugging.'''
    print("\nExample: ID-based debugging")

    # Multiple breakpoints with different IDs
    data = [1, 2, 3, 4, 5]

    cipdb.set_trace(id="start")
    print("Starting processing...")

    for item in data:
        cipdb.set_trace(id="loop")
        result = item * 2

    cipdb.set_trace(id="end")
    print("Processing complete")

    # Run with: CIPDB_ID=loop python demo.py
    # or: CIPDB_IDS=loop,end python demo.py


def example_conditional():
    '''Conditional debugging.'''
    print("\nExample: Conditional debugging")

    users = ['alice', 'bob', 'admin', 'charlie']

    for user in users:
        # Only debug for admin user
        cipdb.set_trace(user == 'admin', id=f"user-{user}")
        print(f"Processing {user}")


def example_environment():
    '''Environment-based debugging.'''
    print("\nExample: Environment debugging")

    # Only debug in development
    cipdb.set_trace(os.getenv("ENV") == "development")

    # Only debug if DEBUG is set
    cipdb.set_trace(os.getenv("DEBUG"))

    print("Environment checks complete")


def example_production_safety():
    '''Production safety patterns.'''
    print("\nExample: Production safety")

    # Method 1: Environment variable
    cipdb.set_trace(os.getenv("DEBUG"))  # Only triggers if DEBUG is set

    # Method 2: Global disable
    if os.environ.get('ENV') == 'production':
        cipdb.disable()

    # Method 3: Set CIPDB=false in production
    # All cipdb calls are disabled when CIPDB=false

    cipdb.set_trace(id="never-in-prod")
    print("Production safe!")


def example_debugging_specific_issue():
    '''Debug a specific issue using IDs.'''
    print("\nExample: Debugging specific issue")

    def process_batch(batch_id, data):
        cipdb.set_trace(id=f"batch-{batch_id}")
        # Complex processing here
        return len(data)

    batches = [
        (1, [1, 2, 3]),
        (2, [4, 5]),
        (3, [6, 7, 8, 9]),
    ]

    for batch_id, data in batches:
        result = process_batch(batch_id, data)
        print(f"Batch {batch_id}: {result} items")

    # Debug only batch 2:
    # CIPDB_ID=batch-2 python demo.py


if __name__ == "__main__":
    print("cipdb Examples")
    print("=" * 40)

    # Uncomment to test different modes:
    # os.environ["DEBUG"] = "true"
    # os.environ["ENV"] = "development"
    # os.environ["CIPDB_ID"] = "loop"

    example_simple()
    example_id_based()
    example_conditional()
    example_environment()
    example_production_safety()
    example_debugging_specific_issue()

    print("\n" + "=" * 40)
    print("Examples complete!")
```

<!-- EOF -->
