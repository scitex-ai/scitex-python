---
name: scientific-figures
description: Universal, library-agnostic standards for publication-quality scientific figures — comparison rules (shared colour scale, aligned axes, consistent sample-size annotations), multi-panel layout grids, colour-map selection for categorical vs continuous vs divergent data, typography and legend placement, PDF-report layout (aspect, DPI, bleed), and how to justify breaking each rule. Pairs with `figrecipe/21_scientific-figure-patterns.md` for matplotlib-specific implementation code. Use when designing any figure for a manuscript, poster, or talk; when reviewing a plot for common pitfalls; or when auditing an ecosystem output for scientific rigour.
canonical-location: scitex-python/src/scitex/_skills/scientific/01_figures_01_standards.md
---

# Scientific Figure Standards (universal principles)

Library-agnostic rules for scientific figures. For figrecipe/matplotlib code
patterns that implement these rules, see
[../../figrecipe/21_scientific-figure-patterns.md](../../figrecipe/21_scientific-figure-patterns.md).

## Comparison Figures: Mandatory Rules

When comparing conditions (treatment vs control, pre vs post, seizure vs
interictal, etc.):

1. **Same color scale.** Both panels MUST share identical `vmin`/`vmax` so
   intensities are directly comparable. Compute the global min/max across all
   compared conditions BEFORE drawing. For diverging data, use a symmetric
   range (`vabs = max(|vmin|, |vmax|)`, then `vmin=-vabs, vmax=vabs`).
2. **Aligned axes.** Use shared x and y across the panels. Remove redundant
   tick labels on inner axes — only label the outer edges.
3. **Side-by-side layout.** Place conditions horizontally (or in a small grid)
   for direct visual comparison. Label each panel clearly with the condition
   name.
4. **Same axis range** on x and y, even if one condition has less data — the
   visual comparison is destroyed by mismatched ranges.
5. **One shared colorbar** for the comparison group (not one per panel) so
   the color↔value mapping is unambiguous.

## Multi-Panel Layout for Per-Subject Reports

- One subject (patient/participant/sample) per page, with all conditions for
  that subject shown together in a grid (e.g., 2×2 or 2×3).
- NOT one figure per page — that explodes page count and breaks comparison.
- Target page count: ~1–2 pages per subject (e.g., 15–25 pages for 15 subjects).

## Temporal Plots with Shared Time Axis

Stack a heatmap above its averaged profile (or any two plots that share time):
- Use a shared x axis for both panels.
- Allocate vertical space proportionally (e.g., heatmap : line ≈ 3 : 1).
- Hide x tick labels on the upper panel; show only on the bottom panel.

## Color Maps

- **Diverging data** (positive/negative around 0): `RdBu_r` or `coolwarm`.
- **Sequential data** (0 → max): `viridis` or `plasma`.
- **Never use `jet`** — perceptually non-uniform; misrepresents data.
- **Always include a colorbar** with units in the label.

## PDF Report Layout

When generating multi-figure scientific reports as a PDF:

- **Bookmarks**: every section navigable via PDF outline (use `fpdf2`'s
  `start_section()` or post-hoc `pikepdf` outline editing).
- **Size**: target under 10MB for email; reduce DPI to 100–150 or compress
  with `ghostscript` if needed.
- **Aspect ratios**: preserve the original aspect ratio of every embedded
  figure — read image dimensions before laying out.
- **Captions**: every figure has a numbered caption (Figure N: …) with a
  one-sentence description.
- **Page numbers** included.

## Anti-patterns

- Two heatmaps with different `vmin`/`vmax` "for clarity" — defeats the
  comparison.
- A diverging colormap centered at the data mean instead of zero — implies
  asymmetry where there isn't any.
- One figure per PDF page for a 50-figure report — unreadable, unprintable.
- Using `jet` "because it's colorful".
