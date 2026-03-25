---
name: str-text-utils
description: General-purpose string utilities — path cleaning, whitespace normalization, ANSI stripping, case conversion (decapitalize, title_case), and API key masking.
---

# Text Utilities

---

## clean_path

Normalize a file system path string by resolving redundant separators and `.`/`..` references.

```python
clean_path(path_string: str) -> str
```

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `path_string` | `str` or path-like | Path to clean |

**Behavior**

- Accepts `str` and any path-like object (`__fspath__` protocol).
- Calls `os.path.normpath` to collapse `.`, `..`, and doubled separators.
- Strips the `f"..."` wrapper if the string starts with `f"`.
- Preserves a trailing `/` if the original path ended with one.
- Raises `ValueError` on failure (wraps the underlying exception).

**Examples**

```python
import scitex as stx

stx.str.clean_path('/home/user/./folder/../file.txt')
# '/home/user/file.txt'

stx.str.clean_path('path/./to//file.txt')
# 'path/to/file.txt'

stx.str.clean_path('/data/runs/')
# '/data/runs/'   (trailing slash preserved)

import pathlib
stx.str.clean_path(pathlib.Path('/tmp/../tmp/data'))
# '/tmp/data'
```

---

## squeeze_spaces

Collapse repeated occurrences of a pattern to a single replacement.

```python
squeeze_spaces(string: str, pattern: str = " +", repl: str = " ") -> str
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `string` | `str` | required | Input string |
| `pattern` | `str` | `" +"` | Regex pattern to collapse |
| `repl` | `str` or callable | `" "` | Replacement value |

Delegates to `re.sub(pattern, repl, string)`.

**Examples**

```python
import scitex as stx

stx.str.squeeze_spaces("Hello   world")
# 'Hello world'

stx.str.squeeze_spaces("a---b--c-d", pattern="-+", repl="-")
# 'a-b-c-d'

stx.str.squeeze_spaces("tab\t\there", pattern=r"\t+", repl="\t")
# 'tab\there'
```

---

## remove_ansi

Strip all ANSI escape sequences from a string (color codes, cursor movement, etc.).

```python
remove_ansi(string: str) -> str
```

Uses the regex `\x1B[@-_][0-?]*[ -/]*[@-~]` to match the full ANSI escape grammar.

**Examples**

```python
import scitex as stx

colored = stx.str.color_text("Hello", "red")   # '\033[91mHello\033[0m'
stx.str.remove_ansi(colored)
# 'Hello'

stx.str.remove_ansi("\033[1;32mGreen bold\033[0m text")
# 'Green bold text'
```

Useful when writing colored terminal output to a log file or comparing strings from `color_text`/`printc`.

---

## decapitalize

Convert only the first character of a string to lowercase, leaving the rest unchanged.

```python
decapitalize(input_string: str) -> str
```

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `input_string` | `str` | String to process |

**Raises** `TypeError` (wrapped as `ValueError`) if input is not a `str`.

**Examples**

```python
import scitex as stx

stx.str.decapitalize("Hello")
# 'hello'

stx.str.decapitalize("WORLD")
# 'wORLD'

stx.str.decapitalize("already lower")
# 'already lower'

stx.str.decapitalize("")
# ''
```

---

## title_case

Convert a string to title case while keeping certain stop words lowercase and preserving all-caps acronyms.

```python
title_case(text: str) -> str
```

**Behavior**

- Splits on whitespace.
- Words that are fully uppercase and more than one character long → kept as-is (treated as acronyms: `CPU`, `EEG`, `AI`).
- Words in the stop-word list → lowercased: `a an the and but or nor at by to in with of on`.
- All other words → `str.capitalize()` (first letter upper, rest lower).

**Examples**

```python
import scitex as stx

stx.str.title_case("welcome to the world of ai and using CPUs for gaming")
# 'Welcome to the World of AI and Using CPUs for Gaming'

stx.str.title_case("the quick brown fox")
# 'the Quick Brown Fox'   (first word 'the' is a stop word → lowercased)

stx.str.title_case("EEG signal processing with FFT")
# 'EEG Signal Processing With FFT'
```

Note: the first word of a sentence is not specially capitalized; if the first word is a stop word it will be lowercase.

---

## mask_api

Mask an API key for safe display in logs and terminal output.

```python
mask_api(api_key: str, n: int = 4) -> str
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | `str` | required | The API key to mask |
| `n` | `int` | `4` | Number of characters to show at each end |

**Returns** `"{first_n}****{last_n}"`.

**Examples**

```python
import scitex as stx

key = "sk-1234567890abcdefghijklmnop"
stx.str.mask_api(key)
# 'sk-1****mnop'

stx.str.mask_api(key, n=6)
# 'sk-123****lmnop'

# Safe logging
import scitex as stx
print(f"Connecting with key: {stx.str.mask_api(api_key)}")
# 'Connecting with key: sk-1****mnop'
```
