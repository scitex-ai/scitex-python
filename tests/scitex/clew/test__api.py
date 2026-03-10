#!/usr/bin/env python3
"""Tests for the minimized clew public API surface."""

import scitex.clew as clew


class TestPublicAPI:
    """Verify __all__ contains exactly 19 public names."""

    def test_all_count(self):
        assert len(clew.__all__) == 19

    def test_all_names(self):
        expected = {
            "status",
            "run",
            "chain",
            "dag",
            "rerun",
            "rerun_dag",
            "rerun_claims",
            "list_runs",
            "stats",
            "add_claim",
            "list_claims",
            "verify_claim",
            "stamp",
            "list_stamps",
            "check_stamp",
            "hash_file",
            "hash_directory",
            "mermaid",
            "init_examples",
        }
        assert set(clew.__all__) == expected

    def test_all_names_are_callable(self):
        for name in clew.__all__:
            assert callable(getattr(clew, name)), f"{name} is not callable"


class TestBackwardCompat:
    """Old names still accessible as attributes (not in __all__)."""

    def test_verify_run(self):
        assert callable(clew.verify_run)

    def test_verify_chain(self):
        assert callable(clew.verify_chain)

    def test_verify_dag(self):
        assert callable(clew.verify_dag)

    def test_verify_by_rerun(self):
        assert callable(clew.verify_by_rerun)

    def test_verify_run_from_scratch(self):
        assert callable(clew.verify_run_from_scratch)

    def test_get_db(self):
        assert callable(clew.get_db)

    def test_set_db(self):
        assert callable(clew.set_db)

    def test_get_status(self):
        assert callable(clew.get_status)

    def test_on_session_start(self):
        assert callable(clew.on_session_start)

    def test_on_session_close(self):
        assert callable(clew.on_session_close)

    def test_on_io_load(self):
        assert callable(clew.on_io_load)

    def test_on_io_save(self):
        assert callable(clew.on_io_save)

    def test_get_tracker(self):
        assert callable(clew.get_tracker)

    def test_format_status(self):
        assert callable(clew.format_status)

    def test_generate_mermaid_dag(self):
        assert callable(clew.generate_mermaid_dag)

    def test_render_dag(self):
        assert callable(clew.render_dag)

    def test_verification_status_enum(self):
        assert hasattr(clew.VerificationStatus, "VERIFIED")

    def test_verification_level_enum(self):
        assert hasattr(clew.VerificationLevel, "CACHE")
        assert hasattr(clew.VerificationLevel, "RERUN")

    def test_classes_accessible(self):
        assert clew.VerificationDB is not None
        assert clew.SessionTracker is not None
        assert clew.ClewRegistry is not None
        assert clew.RunVerification is not None
        assert clew.ChainVerification is not None
        assert clew.DAGVerification is not None
        assert clew.FileVerification is not None
        assert clew.Claim is not None
        assert clew.Stamp is not None

    def test_old_names_not_in_all(self):
        """Old names are accessible but NOT in __all__."""
        old_names = [
            "verify_run",
            "verify_chain",
            "verify_dag",
            "verify_by_rerun",
            "get_db",
            "set_db",
            "get_status",
            "on_session_start",
            "on_session_close",
            "get_tracker",
            "format_status",
            "generate_mermaid_dag",
            "render_dag",
            "VerificationDB",
            "SessionTracker",
            "VerificationStatus",
        ]
        for name in old_names:
            assert name not in clew.__all__, f"{name} should not be in __all__"
            assert hasattr(clew, name), f"{name} should still be accessible"


class TestConvenienceFunctions:
    """Convenience functions delegate to internal implementations."""

    def test_rerun_is_callable(self):
        assert callable(clew.rerun)

    def test_mermaid_is_callable(self):
        assert callable(clew.mermaid)

    def test_rerun_dag_is_callable(self):
        assert callable(clew.rerun_dag)

    def test_rerun_claims_is_callable(self):
        assert callable(clew.rerun_claims)


# EOF
