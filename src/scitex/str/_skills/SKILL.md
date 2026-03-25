---
name: stx.str
description: String utilities for scientific text — LaTeX formatting, color terminal output, axis labels, pattern search, numeric formatting, and general text helpers. Use when formatting plot labels, parsing paths, colorizing output, or handling LaTeX rendering.
---

# stx.str

String utilities for scientific computing. Access via `import scitex as stx` then `stx.str.<function>`.

## Sub-skills

### Color and Print
- [color-print.md](color-print.md) — `color_text` / `ct`, `printc`, `print_debug`: ANSI color codes and bordered block printing

### LaTeX Formatting
- [latex-formatting.md](latex-formatting.md) — `to_latex_style` / `latex_style`, `add_hat_in_latex_style` / `hat_latex_style`: wrap strings in `$...$` math mode and add `\hat{}` notation

### LaTeX Fallback
- [latex-fallback.md](latex-fallback.md) — `safe_latex_render`, `latex_to_mathtext`, `latex_to_unicode`, `latex_fallback_decorator`, `check_latex_capability`, `set_fallback_mode`, `get_latex_status`, `LaTeXFallbackError`: graceful degradation when LaTeX rendering fails

### Plot Text Formatting
- [plot-text.md](plot-text.md) — `format_plot_text`, `format_axis_label` / `axis_label`, `format_title` / `title`, `scientific_text`, `check_unit_consistency`: publication-ready axis labels and titles with unit handling

### Numeric Formatting
- [numeric-formatting.md](numeric-formatting.md) — `factor_out_digits`, `auto_factor_axis`, `smart_tick_formatter`, `readable_bytes`: factor common powers of 10 from tick values and convert byte counts to human-readable strings

### Search and Parsing
- [search-parse.md](search-parse.md) — `grep`, `search`, `parse`, `replace`: regex search in string lists, bidirectional f-string parsing, and template placeholder replacement

### Text Utilities
- [text-utils.md](text-utils.md) — `clean_path`, `squeeze_spaces`, `remove_ansi`, `decapitalize`, `title_case`, `mask_api`: path normalization, whitespace collapse, ANSI stripping, case conversion, and API key masking
