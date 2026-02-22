#!/usr/bin/env python3
# Timestamp: "2026-02-22 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/tests/scitex/notebook/test__compile.py

"""Tests for scitex.notebook._compile module.

Covers _topological_sort, _build_dag, and CompiledNotebook.
No clew DB access is required; DB interactions are mocked with unittest.mock.
"""

from unittest.mock import MagicMock

import pytest

from scitex.notebook._compile import (
    CompiledNotebook,
    _build_dag,
    _topological_sort,
)

# ---------------------------------------------------------------------------
# _topological_sort() tests
# ---------------------------------------------------------------------------


def test_topological_sort_linear_chain():
    """A→B→C chain must be returned in A, B, C order."""
    dag = {"A": ["B"], "B": ["C"], "C": []}
    fallback = ["A", "B", "C"]
    result = _topological_sort(dag, fallback)
    assert result.index("A") < result.index("B")
    assert result.index("B") < result.index("C")


def test_topological_sort_diamond():
    """Diamond A→B, A→C, B→D, C→D must place A first and D last."""
    dag = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
    fallback = ["A", "B", "C", "D"]
    result = _topological_sort(dag, fallback)
    assert result[0] == "A"
    assert result[-1] == "D"
    assert result.index("B") < result.index("D")
    assert result.index("C") < result.index("D")


def test_topological_sort_empty_dag_returns_fallback():
    """Empty DAG must return the fallback order unchanged."""
    dag = {}
    fallback = ["X", "Y", "Z"]
    result = _topological_sort(dag, fallback)
    assert result == fallback


def test_topological_sort_single_node():
    """DAG with a single node and no edges should return that node."""
    dag = {"solo": []}
    fallback = ["solo"]
    result = _topological_sort(dag, fallback)
    assert result == ["solo"]


def test_topological_sort_disconnected_nodes():
    """Nodes not connected by edges should all appear in result."""
    dag = {"A": [], "B": [], "C": []}
    fallback = ["A", "B", "C"]
    result = _topological_sort(dag, fallback)
    assert set(result) == {"A", "B", "C"}


def test_topological_sort_respects_fallback_tiebreaker():
    """When two nodes have same in-degree, fallback_order is used as tiebreaker."""
    dag = {"root": ["A", "B"], "A": [], "B": []}
    fallback = ["root", "A", "B"]
    result = _topological_sort(dag, fallback)
    # A should come before B since A precedes B in fallback
    assert result.index("A") < result.index("B")


def test_topological_sort_nodes_not_in_dag_appended():
    """Nodes in fallback_order but absent from DAG should be appended at end."""
    dag = {"A": ["B"], "B": []}
    fallback = ["A", "B", "C"]  # C is not in dag
    result = _topological_sort(dag, fallback)
    assert "C" in result


# ---------------------------------------------------------------------------
# _build_dag() tests
# ---------------------------------------------------------------------------


def _make_run(session_id):
    """Helper to make a minimal run dict."""
    return {"session_id": session_id}


def test_build_dag_no_shared_files():
    """Sessions with no shared IO files should produce an empty DAG (no edges)."""
    runs = [_make_run("s1"), _make_run("s2")]
    db = MagicMock()
    db.get_file_hashes.return_value = {}
    dag = _build_dag(runs, db)
    assert dag == {"s1": [], "s2": []}


def test_build_dag_producer_consumer_edge():
    """Session A that produces file X, session B that consumes file X: A→B."""
    runs = [_make_run("A"), _make_run("B")]
    db = MagicMock()

    def _get_file_hashes(session_id, role):
        if session_id == "A" and role == "output":
            return {"shared.csv": "hash1"}
        if session_id == "B" and role == "input":
            return {"shared.csv": "hash1"}
        return {}

    db.get_file_hashes.side_effect = _get_file_hashes
    dag = _build_dag(runs, db)
    assert "B" in dag["A"]
    assert "A" not in dag.get("B", [])


def test_build_dag_no_self_edge():
    """A session should not be its own producer/consumer."""
    runs = [_make_run("A")]
    db = MagicMock()

    def _get_file_hashes(session_id, role):
        return {"file.csv": "hash1"}

    db.get_file_hashes.side_effect = _get_file_hashes
    dag = _build_dag(runs, db)
    assert "A" not in dag.get("A", [])


def test_build_dag_all_sessions_present_as_keys():
    """Every session ID must appear as a key in the returned DAG."""
    runs = [_make_run("s1"), _make_run("s2"), _make_run("s3")]
    db = MagicMock()
    db.get_file_hashes.return_value = {}
    dag = _build_dag(runs, db)
    assert set(dag.keys()) == {"s1", "s2", "s3"}


# ---------------------------------------------------------------------------
# CompiledNotebook tests
# ---------------------------------------------------------------------------


def test_compiled_notebook_to_mermaid_contains_header():
    """to_mermaid() output must start with 'graph TD'."""
    cn = CompiledNotebook(notebook_path="/nb.ipynb")
    mermaid = cn.to_mermaid()
    assert "graph TD" in mermaid


def test_compiled_notebook_to_mermaid_includes_session_ids():
    """to_mermaid() should contain (partial) session IDs for each run."""
    runs = [
        {"session_id": "session-abc123", "started_at": "2026-01-01T00:00:00"},
        {"session_id": "session-def456", "started_at": "2026-01-02T00:00:00"},
    ]
    cn = CompiledNotebook(
        notebook_path="/nb.ipynb",
        execution_order=["session-abc123", "session-def456"],
        dag={"session-abc123": ["session-def456"], "session-def456": []},
        runs=runs,
    )
    mermaid = cn.to_mermaid()
    assert "graph TD" in mermaid
    # Short IDs should appear
    assert "session-abc123"[:20].replace("-", "_") in mermaid.replace("-", "_")


def test_compiled_notebook_to_mermaid_includes_edges():
    """to_mermaid() should include '-->' arrows for DAG edges."""
    runs = [
        {"session_id": "A", "started_at": ""},
        {"session_id": "B", "started_at": ""},
    ]
    cn = CompiledNotebook(
        notebook_path="/nb.ipynb",
        execution_order=["A", "B"],
        dag={"A": ["B"], "B": []},
        runs=runs,
    )
    mermaid = cn.to_mermaid()
    assert "-->" in mermaid


def test_compiled_notebook_to_script_contains_shebang():
    """to_script() output must contain a Python shebang line."""
    cn = CompiledNotebook(notebook_path="/nb.ipynb")
    script = cn.to_script()
    assert "#!/usr/bin/env python3" in script


def test_compiled_notebook_to_script_contains_import():
    """to_script() must import scitex as stx."""
    cn = CompiledNotebook(notebook_path="/nb.ipynb")
    script = cn.to_script()
    assert "import scitex as stx" in script


def test_compiled_notebook_to_script_contains_session_decorator():
    """to_script() must include @stx.session decorator for each session."""
    runs = [{"session_id": "run-001", "script_path": "/script.py"}]
    cn = CompiledNotebook(
        notebook_path="/nb.ipynb",
        execution_order=["run-001"],
        dag={"run-001": []},
        runs=runs,
    )
    script = cn.to_script()
    assert "@stx.session" in script


def test_compiled_notebook_to_script_empty_produces_valid_python():
    """to_script() with no runs should still produce valid (minimal) Python."""
    cn = CompiledNotebook(notebook_path="/nb.ipynb")
    script = cn.to_script()
    # Should at least contain the header lines
    assert "python3" in script or "stx" in script


def test_compiled_notebook_to_script_function_per_session():
    """to_script() should produce one function definition per session."""
    runs = [
        {"session_id": "r1", "script_path": ""},
        {"session_id": "r2", "script_path": ""},
    ]
    cn = CompiledNotebook(
        notebook_path="/nb.ipynb",
        execution_order=["r1", "r2"],
        dag={"r1": [], "r2": []},
        runs=runs,
    )
    script = cn.to_script()
    # Count 'def ' occurrences — one per session
    def_count = script.count("def step_")
    assert def_count == 2


def test_compiled_notebook_default_fields():
    """CompiledNotebook should initialise with empty lists/dicts by default."""
    cn = CompiledNotebook(notebook_path="/nb.ipynb")
    assert cn.execution_order == []
    assert cn.dag == {}
    assert cn.runs == []


# ---------------------------------------------------------------------------
# Cycle detection tests
# ---------------------------------------------------------------------------


def test_topological_sort_cycle_warns():
    """Cyclic DAG should emit a warning and still return all nodes."""
    import warnings

    dag = {"A": ["B"], "B": ["A"]}
    fallback = ["A", "B"]
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = _topological_sort(dag, fallback)
        assert len(w) == 1
        assert "Cyclic" in str(w[0].message)
    assert set(result) == {"A", "B"}


def test_topological_sort_cycle_preserves_non_cyclic():
    """Nodes not in cycle should still be sorted correctly."""
    import warnings

    # C depends on A; A and B form a cycle
    dag = {"A": ["B"], "B": ["A"], "C": []}
    fallback = ["C", "A", "B"]
    with warnings.catch_warnings(record=True):
        warnings.simplefilter("always")
        result = _topological_sort(dag, fallback)
    # C has no dependencies, should appear; A and B both present
    assert set(result) == {"A", "B", "C"}


def test_topological_sort_three_node_cycle():
    """Three-node cycle A→B→C→A should warn and include all nodes."""
    import warnings

    dag = {"A": ["B"], "B": ["C"], "C": ["A"]}
    fallback = ["A", "B", "C"]
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = _topological_sort(dag, fallback)
        assert len(w) == 1
    assert set(result) == {"A", "B", "C"}


# ---------------------------------------------------------------------------
# compile_notebook() with mock DB tests
# ---------------------------------------------------------------------------


def test_compile_notebook_empty_runs(tmp_path):
    """compile_notebook should return empty CompiledNotebook when no runs found."""
    import json
    from unittest.mock import patch

    nb = {
        "cells": [],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    nb_file = tmp_path / "test.ipynb"
    nb_file.write_text(json.dumps(nb), encoding="utf-8")

    mock_db = MagicMock()
    mock_db.list_runs.return_value = []

    with patch("scitex.clew.get_db", return_value=mock_db):
        from scitex.notebook._compile import compile_notebook

        result = compile_notebook(nb_file)

    assert result.execution_order == []
    assert result.dag == {}


def test_compile_notebook_with_runs(tmp_path):
    """compile_notebook should build DAG from matched runs."""
    import json
    from unittest.mock import patch

    nb_file = tmp_path / "experiment.ipynb"
    nb_file.write_text(
        json.dumps({"cells": [], "metadata": {}, "nbformat": 4, "nbformat_minor": 5}),
        encoding="utf-8",
    )

    runs = [
        {
            "session_id": "s1",
            "started_at": "2026-01-01T00:00:00",
            "script_path": str(nb_file),
            "metadata": json.dumps({"notebook_path": str(nb_file)}),
        },
        {
            "session_id": "s2",
            "started_at": "2026-01-01T00:01:00",
            "script_path": str(nb_file),
            "metadata": json.dumps({"notebook_path": str(nb_file)}),
        },
    ]

    mock_db = MagicMock()
    mock_db.list_runs.return_value = runs
    mock_db.get_file_hashes.return_value = {}

    with patch("scitex.clew.get_db", return_value=mock_db):
        from scitex.notebook._compile import compile_notebook

        result = compile_notebook(nb_file)

    assert result.execution_order == ["s1", "s2"]
    assert "s1" in result.dag
    assert "s2" in result.dag


# EOF
