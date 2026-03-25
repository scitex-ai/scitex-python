---
description: ANSI color text and colored block printing utilities — color_text (alias ct), printc, print_debug.
---

# Color Text and Printing

## color_text / ct

Apply ANSI terminal color codes to a string. `ct` is an alias for `color_text`.

```python
color_text(text, c="green") -> str
ct(text, c="green") -> str
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `text` | `str` | required | Text to colorize |
| `c` | `str` | `"green"` | Color name |

**Available colors**

| Name | Effect | Semantic alias |
|------|--------|---------------|
| `"red"` | `\033[91m` | `"tes"` (test) |
| `"green"` | `\033[92m` | `"val"` (validation) |
| `"yellow"` | `\033[93m` | — |
| `"blue"` | `\033[94m` | — |
| `"magenta"` | `\033[95m` | — |
| `"cyan"` | `\033[96m` | — |
| `"white"` | `\033[97m` | `"tra"` (training) |
| `"grey"` / `"gray"` | `\033[90m` | — |
| `"reset"` | `\033[0m` | — |

**Examples**

```python
import scitex as stx

print(stx.str.color_text("Hello!", "blue"))   # blue terminal output
print(stx.str.ct("Error!", "red"))            # short alias
print(stx.str.ct("Train loss:", "tra"))       # semantic alias for white
```

**Returns** the original string wrapped in ANSI escape sequences. The text renders in color on ANSI-capable terminals; on others the escape codes appear as literal characters.

---

## printc

Print a message surrounded by a repeated-character border, optionally colored.

```python
printc(message, c="blue", char="-", n=40) -> None
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `message` | `str` | required | Message to display |
| `c` | `str` | `"blue"` | Border color (same names as `color_text`); `None` disables color |
| `char` | `str` | `"-"` | Character used to build the border line; `None` omits the border |
| `n` | `int` | `40` | Width of the border (number of repetitions of `char`) |

**Behavior**

- With `char` and `c`: prints `\n{border}\n{message}\n{border}\n` in the chosen color.
- With `char=None`: prints `\n{message}\n` (no border), still colored if `c` is set.
- With `c=None`: no color applied.

**Examples**

```python
import scitex as stx

stx.str.printc("Section start")
# ----------------------------------------
# Section start
# ----------------------------------------
# (in blue)

stx.str.printc("WARNING", c="yellow", char="*", n=30)
# ******************************
# WARNING
# ******************************
# (in yellow)

stx.str.printc("Plain message", char=None, c=None)
#
# Plain message
#
```

---

## print_debug

Print a high-visibility DEBUG MODE banner in yellow. Takes no arguments. Useful at the start of debug-mode execution to make debug runs immediately distinguishable.

```python
print_debug() -> None
```

**Output** (in yellow):

```
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! (× many lines)
!!!!!!!!!!!!!!!!!!!!!! DEBUG MODE !!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! (× many lines)
```

**Example**

```python
import scitex as stx

DEBUG = True
if DEBUG:
    stx.str.print_debug()
    # Visible yellow banner in terminal
```
