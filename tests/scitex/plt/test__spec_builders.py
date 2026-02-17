#!/usr/bin/env python3
# Timestamp: "2026-02-17 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/tests/scitex/plt/test__spec_builders.py
"""Tests for scitex.plt._spec_builders."""

import pytest

from scitex.plt._spec_builders import (
    ALL_KINDS,
    DATA_KINDS,
    KIND_ALIASES,
    LABEL_KINDS,
    MATRIX_KINDS,
    XY_KINDS,
    build_spec,
    build_spec_from_csv,
)


class TestKindRegistries:
    def test_all_kinds_is_union(self):
        assert ALL_KINDS == XY_KINDS | DATA_KINDS | LABEL_KINDS | MATRIX_KINDS

    def test_aliases_resolve_to_valid_kinds(self):
        for alias, canonical in KIND_ALIASES.items():
            assert canonical in ALL_KINDS


class TestBuildSpec:
    def test_missing_kind_raises(self):
        with pytest.raises(ValueError, match="kind"):
            build_spec({})

    def test_unsupported_kind_raises(self):
        with pytest.raises(ValueError, match="Unsupported kind"):
            build_spec({"kind": "nonexistent"})

    def test_line_spec(self):
        spec = build_spec({"kind": "line", "y": "1,2,3"})
        assert spec["plots"][0]["type"] == "line"
        assert spec["plots"][0]["y"] == [1.0, 2.0, 3.0]

    def test_line_with_x(self):
        spec = build_spec({"kind": "scatter", "x": "10,20,30", "y": "1,2,3"})
        assert spec["plots"][0]["x"] == [10.0, 20.0, 30.0]
        assert spec["plots"][0]["y"] == [1.0, 2.0, 3.0]

    def test_categorical_x_creates_xticks(self):
        spec = build_spec({"kind": "bar", "x": "A,B,C", "y": "1,2,3"})
        assert "xticks" in spec
        assert spec["xticks"]["labels"] == ["A", "B", "C"]

    def test_xy_requires_y(self):
        with pytest.raises(ValueError, match="'y' parameter is required"):
            build_spec({"kind": "line"})

    def test_box_alias(self):
        spec = build_spec({"kind": "box", "data": "1,2,3,4,5"})
        assert spec["plots"][0]["type"] == "boxplot"

    def test_violin_alias(self):
        spec = build_spec({"kind": "violin", "data": "1,2,3,4,5"})
        assert spec["plots"][0]["type"] == "violinplot"

    def test_distribution_multiple_groups(self):
        spec = build_spec(
            {
                "kind": "boxplot",
                "data": "1,2,3",
                "data2": "4,5,6",
            }
        )
        assert len(spec["plots"][0]["data"]) == 2

    def test_hist_single_group(self):
        spec = build_spec({"kind": "hist", "data": "1,2,3,4,5"})
        assert spec["plots"][0]["x"] == [1.0, 2.0, 3.0, 4.0, 5.0]

    def test_pie(self):
        spec = build_spec({"kind": "pie", "data": "30,40,30", "labels": "A,B,C"})
        assert spec["plots"][0]["x"] == [30.0, 40.0, 30.0]
        assert spec["plots"][0]["labels"] == ["A", "B", "C"]

    def test_pie_requires_data(self):
        with pytest.raises(ValueError, match="'data' parameter is required"):
            build_spec({"kind": "pie"})

    def test_heatmap(self):
        spec = build_spec(
            {
                "kind": "heatmap",
                "data": "1,2,3,4",
                "nrows": "2",
                "ncols": "2",
            }
        )
        assert spec["plots"][0]["data"] == [[1.0, 2.0], [3.0, 4.0]]
        assert spec["plots"][0]["type"] == "imshow"

    def test_heatmap_auto_reshape(self):
        spec = build_spec({"kind": "heatmap", "data": "1,2,3,4"})
        assert spec["plots"][0]["type"] == "imshow"
        assert len(spec["plots"][0]["data"]) == 2

    def test_styling_params(self):
        spec = build_spec(
            {
                "kind": "line",
                "y": "1,2,3",
                "color": "red",
                "title": "My Title",
                "xlabel": "X",
                "ylabel": "Y",
            }
        )
        assert spec["plots"][0]["color"] == "red"
        assert spec["title"] == "My Title"
        assert spec["xlabel"] == "X"
        assert spec["ylabel"] == "Y"

    def test_figure_dimensions(self):
        spec = build_spec({"kind": "line", "y": "1,2", "width": "100", "height": "80"})
        assert spec["figure"]["width_mm"] == 100
        assert spec["figure"]["height_mm"] == 80

    def test_yerr_promotes_to_errorbar(self):
        spec = build_spec({"kind": "line", "y": "1,2,3", "yerr": "0.1,0.2,0.3"})
        assert spec["plots"][0]["type"] == "errorbar"
        assert spec["plots"][0]["yerr"] == [0.1, 0.2, 0.3]


class TestBuildSpecFromCsv:
    def test_xy_from_csv(self):
        spec = build_spec_from_csv(
            "/tmp/data.csv",
            {"kind": "scatter", "x_col": "time", "y_col": "value"},
        )
        assert spec["plots"][0]["data_file"] == "/tmp/data.csv"
        assert spec["plots"][0]["x"] == "time"
        assert spec["plots"][0]["y"] == "value"

    def test_requires_y_col(self):
        with pytest.raises(ValueError, match="y_col"):
            build_spec_from_csv("/tmp/d.csv", {"kind": "line"})

    def test_distribution_from_csv(self):
        spec = build_spec_from_csv(
            "/tmp/d.csv",
            {"kind": "hist", "data_col": "values"},
        )
        assert spec["plots"][0]["x"] == "values"

    def test_pie_from_csv(self):
        spec = build_spec_from_csv(
            "/tmp/d.csv",
            {"kind": "pie", "data_col": "sizes", "labels_col": "names"},
        )
        assert spec["plots"][0]["x"] == "sizes"
        assert spec["plots"][0]["labels"] == "names"

    def test_heatmap_from_csv(self):
        spec = build_spec_from_csv(
            "/tmp/d.csv",
            {"kind": "heatmap", "data_col": "matrix"},
        )
        assert spec["plots"][0]["type"] == "imshow"
        assert spec["plots"][0]["data"] == "matrix"


# EOF
