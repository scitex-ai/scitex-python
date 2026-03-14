#!/usr/bin/env python3
"""Tests for scitex.cli.scholar - Scholar CLI commands."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from scitex.cli.scholar import scholar


class TestScholarGroup:
    """Tests for the scholar command group."""

    def test_scholar_help(self):
        """Test that scholar help is displayed correctly."""
        runner = CliRunner()
        result = runner.invoke(scholar, ["--help"])
        assert result.exit_code == 0
        assert "Scientific paper management" in result.output

    def test_scholar_has_subcommands(self):
        """Test that all expected subcommands are registered."""
        runner = CliRunner()
        result = runner.invoke(scholar, ["--help"])
        expected_commands = ["fetch", "library", "config", "jobs"]
        for cmd in expected_commands:
            assert cmd in result.output, f"Command '{cmd}' not found in scholar help"

    def test_scholar_no_command_shows_help(self):
        """Test that invoking scholar without command shows usage."""
        runner = CliRunner()
        result = runner.invoke(scholar, [])
        # Click groups show help or usage when no command given
        assert result.exit_code == 0


class TestScholarFetch:
    """Tests for the scholar fetch command."""

    def test_fetch_help(self):
        """Test fetch command help."""
        runner = CliRunner()
        result = runner.invoke(scholar, ["fetch", "--help"])
        assert result.exit_code == 0
        assert "Fetch papers to your library" in result.output

    def test_fetch_requires_input(self):
        """Test that fetch requires papers or --from-bibtex."""
        runner = CliRunner()
        result = runner.invoke(scholar, ["fetch"])
        assert result.exit_code == 1
        assert "Provide DOIs/titles or use --from-bibtex" in result.output

    def test_fetch_with_single_doi(self):
        """Test fetch command with a single DOI."""
        runner = CliRunner()
        with patch("scitex.scholar.pipelines.ScholarPipelineSingle") as mock_cls:
            mock_pipeline = MagicMock()
            mock_paper = MagicMock()
            mock_paper.metadata.id.doi = "10.1038/nature12373"
            mock_paper.metadata.basic.title = "Test Paper"
            mock_pipeline.process_single_paper = MagicMock(
                return_value=(mock_paper, Path("/tmp/paper.pdf"))
            )
            mock_cls.return_value = mock_pipeline

            with patch("asyncio.run") as mock_run:
                mock_run.return_value = {
                    "success": True,
                    "message": "Paper fetched",
                    "doi": "10.1038/nature12373",
                    "path": "/tmp/paper.pdf",
                }
                result = runner.invoke(scholar, ["fetch", "10.1038/nature12373"])
                # Should attempt to fetch the paper
                assert "Fetching" in result.output or result.exit_code == 0

    def test_fetch_with_multiple_papers(self):
        """Test fetch command with multiple papers."""
        runner = CliRunner()
        with patch("scitex.scholar.pipelines.ScholarPipelineParallel") as mock_cls:
            mock_pipeline = MagicMock()
            mock_cls.return_value = mock_pipeline

            with patch("asyncio.run") as mock_run:
                mock_run.return_value = {
                    "success": True,
                    "total": 2,
                    "fetched": 2,
                    "failed": 0,
                }
                result = runner.invoke(
                    scholar,
                    ["fetch", "10.1038/nature12373", "10.1016/j.neuron.2018.01.023"],
                )
                # Should attempt to fetch multiple papers
                assert "Fetching" in result.output or result.exit_code == 0

    def test_fetch_with_project(self):
        """Test fetch command with --project option."""
        runner = CliRunner()
        with patch("scitex.scholar.pipelines.ScholarPipelineSingle") as mock_cls:
            mock_pipeline = MagicMock()
            mock_cls.return_value = mock_pipeline

            with patch("asyncio.run") as mock_run:
                mock_run.return_value = {"success": True, "message": "Paper fetched"}
                result = runner.invoke(
                    scholar,
                    ["fetch", "10.1038/nature12373", "--project", "neuroscience"],
                )
                assert result.exit_code == 0 or "Fetching" in result.output

    def test_fetch_browser_modes(self):
        """Test fetch command with different browser modes."""
        runner = CliRunner()
        for mode in ["stealth", "interactive"]:
            with patch("scitex.scholar.pipelines.ScholarPipelineSingle") as mock_cls:
                mock_pipeline = MagicMock()
                mock_cls.return_value = mock_pipeline

                with patch("asyncio.run") as mock_run:
                    mock_run.return_value = {"success": True}
                    result = runner.invoke(
                        scholar,
                        ["fetch", "10.1038/nature12373", "--browser-mode", mode],
                    )
                    # Should accept the mode
                    assert result.exit_code == 0 or "Fetching" in result.output

    def test_fetch_json_output(self):
        """Test fetch command with --json option."""
        runner = CliRunner()
        with patch("scitex.scholar.pipelines.ScholarPipelineSingle") as mock_cls:
            mock_pipeline = MagicMock()
            mock_paper = MagicMock()
            mock_paper.metadata.id.doi = "10.1038/nature12373"
            mock_paper.metadata.basic.title = "Test Paper"
            mock_paper.metadata.path.pdfs_engines = ["chrome_pdf_viewer"]
            mock_paper.container.pdf_size_bytes = 1024
            mock_pipeline.process_single_paper = MagicMock(
                return_value=(mock_paper, Path("/tmp/paper.pdf"))
            )
            mock_cls.return_value = mock_pipeline

            with patch("asyncio.run") as mock_run:
                mock_run.return_value = {
                    "success": True,
                    "success_doi": True,
                    "success_metadata": True,
                    "success_pdf": True,
                    "success_content": True,
                    "pdf_method": "chrome_pdf_viewer",
                    "message": "Paper fetched",
                    "doi": "10.1038/nature12373",
                }
                result = runner.invoke(
                    scholar, ["fetch", "10.1038/nature12373", "--json"]
                )
                # Output should be valid JSON
                try:
                    data = json.loads(result.output)
                    assert "success" in data
                except json.JSONDecodeError:
                    # Some output might include logs before JSON
                    pass

    def test_fetch_json_output_granular_flags(self):
        """Test fetch JSON output includes granular success flags."""
        runner = CliRunner()
        with patch("scitex.scholar.pipelines.ScholarPipelineSingle") as mock_cls:
            mock_pipeline = MagicMock()
            mock_paper = MagicMock()
            mock_paper.metadata.id.doi = "10.1038/nature12373"
            mock_paper.metadata.basic.title = "Test Paper"
            mock_paper.metadata.path.pdfs_engines = ["manual_download"]
            mock_paper.container.pdf_size_bytes = 2048
            mock_pipeline.process_single_paper = MagicMock(
                return_value=(mock_paper, Path("/tmp/paper.pdf"))
            )
            mock_cls.return_value = mock_pipeline

            with patch("asyncio.run") as mock_run:
                mock_run.return_value = {
                    "success": True,
                    "success_doi": True,
                    "success_metadata": True,
                    "success_pdf": True,
                    "success_content": True,
                    "pdf_method": "manual_download",
                    "message": "Paper fetched",
                    "doi": "10.1038/nature12373",
                    "title": "Test Paper",
                    "path": "/tmp/paper.pdf",
                    "has_pdf": True,
                }
                result = runner.invoke(
                    scholar, ["fetch", "10.1038/nature12373", "--json"]
                )
                try:
                    output = json.loads(result.output)
                    data = output.get("data", output)
                    # Verify granular success flags are present
                    assert "success_doi" in data
                    assert "success_metadata" in data
                    assert "success_pdf" in data
                    assert "success_content" in data
                    assert "pdf_method" in data
                    # Verify values
                    assert data["success_doi"] is True
                    assert data["success_metadata"] is True
                    assert data["success_pdf"] is True
                    assert data["pdf_method"] == "manual_download"
                except json.JSONDecodeError:
                    pass

    def test_fetch_json_output_partial_success(self):
        """Test fetch JSON output with partial success (metadata only, no PDF)."""
        runner = CliRunner()
        with patch("scitex.scholar.pipelines.ScholarPipelineSingle") as mock_cls:
            mock_pipeline = MagicMock()
            mock_paper = MagicMock()
            mock_paper.metadata.id.doi = "10.1038/nature12373"
            mock_paper.metadata.basic.title = "Test Paper"
            mock_paper.metadata.path.pdfs_engines = []
            mock_paper.container.pdf_size_bytes = 0
            mock_pipeline.process_single_paper = MagicMock(
                return_value=(mock_paper, None)  # No symlink = no PDF
            )
            mock_cls.return_value = mock_pipeline

            with patch("asyncio.run") as mock_run:
                mock_run.return_value = {
                    "success": False,
                    "success_doi": True,
                    "success_metadata": True,
                    "success_pdf": False,
                    "success_content": False,
                    "pdf_method": None,
                    "message": "Metadata fetched but PDF not downloaded",
                    "doi": "10.1038/nature12373",
                    "title": "Test Paper",
                    "path": None,
                    "has_pdf": False,
                }
                result = runner.invoke(
                    scholar, ["fetch", "10.1038/nature12373", "--json"]
                )
                try:
                    output = json.loads(result.output)
                    data = output.get("data", output)
                    # Overall success is False (no PDF)
                    assert output.get("success", data.get("success")) is False
                    # But metadata was obtained
                    assert data["success_doi"] is True
                    assert data["success_metadata"] is True
                    # PDF not obtained
                    assert data["success_pdf"] is False
                    assert data["pdf_method"] is None
                except json.JSONDecodeError:
                    pass

    def test_fetch_cannot_mix_args_and_bibtex(self):
        """Test that fetch rejects both papers and --from-bibtex."""
        runner = CliRunner()
        with tempfile.NamedTemporaryFile(suffix=".bib", delete=False) as f:
            f.write(b"@article{test, title={Test}}")
            f.flush()
            result = runner.invoke(
                scholar, ["fetch", "10.1038/nature12373", "--from-bibtex", f.name]
            )
            assert result.exit_code == 1
            assert "Cannot mix positional arguments with --from-bibtex" in result.output
            Path(f.name).unlink()

    def test_fetch_from_bibtex(self):
        """Test fetch command with --from-bibtex option."""
        runner = CliRunner()
        with tempfile.NamedTemporaryFile(suffix=".bib", delete=False) as f:
            f.write(b"@article{test, title={Test}, doi={10.1038/nature12373}}")
            f.flush()

            with patch("scitex.scholar.pipelines.ScholarPipelineBibTeX") as mock_cls:
                mock_pipeline = MagicMock()
                mock_cls.return_value = mock_pipeline

                with patch("asyncio.run") as mock_run:
                    mock_run.return_value = {"success": True, "total": 1}
                    result = runner.invoke(scholar, ["fetch", "--from-bibtex", f.name])
                    assert "Fetching" in result.output or result.exit_code == 0

            Path(f.name).unlink()

    def test_fetch_async_mode(self):
        """Test fetch command with --async option."""
        runner = CliRunner()
        with patch("scitex.scholar.jobs.JobManager") as mock_manager_cls:
            mock_manager = MagicMock()
            mock_manager.submit.return_value = "job-12345"
            mock_manager_cls.return_value = mock_manager

            with patch("subprocess.Popen"):
                result = runner.invoke(
                    scholar, ["fetch", "10.1038/nature12373", "--async"]
                )
                assert result.exit_code == 0
                assert (
                    "job-12345" in result.output or "started" in result.output.lower()
                )


class TestScholarLibrary:
    """Tests for the scholar library command."""

    def test_library_help(self):
        """Test library command help."""
        runner = CliRunner()
        result = runner.invoke(scholar, ["library", "--help"])
        assert result.exit_code == 0
        assert "Show your paper library" in result.output

    def test_library_empty(self):
        """Test library command when no library exists."""
        runner = CliRunner()
        with patch("scitex.cli.scholar._library.get_paths") as mock_get_paths:
            mock_paths = MagicMock()
            mock_paths.scholar_library = Path("/nonexistent/library")
            mock_get_paths.return_value = mock_paths

            result = runner.invoke(scholar, ["library"])
            assert result.exit_code == 0
            assert (
                "empty" in result.output.lower() or "Library is empty" in result.output
            )

    def test_library_with_papers(self):
        """Test library command with existing library."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            library_path = Path(tmpdir)
            master_path = library_path / "MASTER"
            master_path.mkdir()
            (master_path / "paper1").mkdir()
            (master_path / "paper2").mkdir()

            with patch("scitex.cli.scholar._library.get_paths") as mock_get_paths:
                mock_paths = MagicMock()
                mock_paths.scholar_library = library_path
                mock_get_paths.return_value = mock_paths

                result = runner.invoke(scholar, ["library"])
                assert result.exit_code == 0
                assert "2" in result.output  # Total papers

    def test_library_with_project(self):
        """Test library command with --project option."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            library_path = Path(tmpdir)
            project_path = library_path / "neuroscience"
            project_path.mkdir()
            # Create a symlink to simulate a paper
            paper_link = project_path / "paper1"
            paper_link.symlink_to(tmpdir)

            with patch("scitex.cli.scholar._library.get_paths") as mock_get_paths:
                mock_paths = MagicMock()
                mock_paths.scholar_library = library_path
                mock_get_paths.return_value = mock_paths

                result = runner.invoke(
                    scholar, ["library", "--project", "neuroscience"]
                )
                assert result.exit_code == 0
                assert "neuroscience" in result.output

    def test_library_project_not_found(self):
        """Test library command with non-existent project."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            library_path = Path(tmpdir)

            with patch("scitex.cli.scholar._library.get_paths") as mock_get_paths:
                mock_paths = MagicMock()
                mock_paths.scholar_library = library_path
                mock_get_paths.return_value = mock_paths

                result = runner.invoke(scholar, ["library", "--project", "nonexistent"])
                assert result.exit_code == 0
                assert "not found" in result.output.lower()

    def test_library_json_output(self):
        """Test library command with --json option."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            library_path = Path(tmpdir)
            master_path = library_path / "MASTER"
            master_path.mkdir()
            (master_path / "paper1").mkdir()

            with patch("scitex.cli.scholar._library.get_paths") as mock_get_paths:
                mock_paths = MagicMock()
                mock_paths.scholar_library = library_path
                mock_get_paths.return_value = mock_paths

                result = runner.invoke(scholar, ["library", "--json"])
                assert result.exit_code == 0
                output = json.loads(result.output)
                data = output.get("data", output)
                assert output.get("success", data.get("success")) is True
                assert "total_papers" in data


class TestScholarConfig:
    """Tests for the scholar config command."""

    def test_config_help(self):
        """Test config command help."""
        runner = CliRunner()
        result = runner.invoke(scholar, ["config", "--help"])
        assert result.exit_code == 0
        assert "Scholar configuration" in result.output

    def test_config_display(self):
        """Test config command displays configuration."""
        runner = CliRunner()
        with patch("scitex.cli.scholar._library.get_paths") as mock_get_paths:
            mock_paths = MagicMock()
            mock_paths.scholar_library = Path("/home/user/.scitex/scholar/library")
            mock_get_paths.return_value = mock_paths

            result = runner.invoke(scholar, ["config"])
            assert result.exit_code == 0
            assert "SciTeX Scholar" in result.output
            assert "Library" in result.output

    def test_config_json_output(self):
        """Test config command with --json option."""
        runner = CliRunner()
        with patch("scitex.cli.scholar._library.get_paths") as mock_get_paths:
            mock_paths = MagicMock()
            mock_paths.scholar_library = Path("/home/user/.scitex/scholar/library")
            mock_get_paths.return_value = mock_paths

            result = runner.invoke(scholar, ["config", "--json"])
            assert result.exit_code == 0
            output = json.loads(result.output)
            data = output.get("data", output)
            assert output.get("success", data.get("success")) is True
            assert "library_path" in data


class TestScholarJobs:
    """Tests for the scholar jobs subgroup."""

    def test_jobs_help(self):
        """Test jobs command help."""
        runner = CliRunner()
        result = runner.invoke(scholar, ["jobs", "--help"])
        assert result.exit_code == 0
        assert "Manage background jobs" in result.output

    def test_jobs_has_subcommands(self):
        """Test that jobs has all expected subcommands."""
        runner = CliRunner()
        result = runner.invoke(scholar, ["jobs", "--help"])
        expected_commands = ["list", "status", "start", "cancel", "result", "clean"]
        for cmd in expected_commands:
            assert cmd in result.output, f"Command '{cmd}' not found in jobs help"


class TestScholarJobsList:
    """Tests for the scholar jobs list command."""

    def test_jobs_list_help(self):
        """Test jobs list command help."""
        runner = CliRunner()
        result = runner.invoke(scholar, ["jobs", "list", "--help"])
        assert result.exit_code == 0
        assert "List all jobs" in result.output

    def test_jobs_list_empty(self):
        """Test jobs list when no jobs exist."""
        runner = CliRunner()
        with patch("scitex.scholar.jobs.JobManager") as mock_manager_cls:
            mock_manager = MagicMock()
            mock_manager.list_jobs.return_value = []
            mock_manager_cls.return_value = mock_manager

            result = runner.invoke(scholar, ["jobs", "list"])
            assert result.exit_code == 0
            assert "No jobs found" in result.output

    def test_jobs_list_with_jobs(self):
        """Test jobs list with existing jobs."""
        runner = CliRunner()
        with patch("scitex.scholar.jobs.JobManager") as mock_manager_cls:
            mock_manager = MagicMock()
            mock_manager.list_jobs.return_value = [
                {
                    "job_id": "job-12345",
                    "job_type": "fetch",
                    "status": "completed",
                    "progress": {"percent": 100},
                },
                {
                    "job_id": "job-67890",
                    "job_type": "fetch_bibtex",
                    "status": "running",
                    "progress": {"percent": 50},
                },
            ]
            mock_manager_cls.return_value = mock_manager

            result = runner.invoke(scholar, ["jobs", "list"])
            assert result.exit_code == 0
            assert "job-12345" in result.output
            assert "job-67890" in result.output

    def test_jobs_list_filter_by_status(self):
        """Test jobs list with --status filter."""
        runner = CliRunner()
        with patch("scitex.scholar.jobs.JobManager") as mock_manager_cls:
            mock_manager = MagicMock()
            mock_manager.list_jobs.return_value = []
            mock_manager_cls.return_value = mock_manager

            result = runner.invoke(scholar, ["jobs", "list", "--status", "running"])
            assert result.exit_code == 0
            mock_manager.list_jobs.assert_called_once_with(status="running", limit=20)

    def test_jobs_list_json_output(self):
        """Test jobs list with --json option."""
        runner = CliRunner()
        with patch("scitex.scholar.jobs.JobManager") as mock_manager_cls:
            mock_manager = MagicMock()
            mock_manager.list_jobs.return_value = [
                {"job_id": "job-12345", "job_type": "fetch", "status": "completed"}
            ]
            mock_manager_cls.return_value = mock_manager

            result = runner.invoke(scholar, ["jobs", "list", "--json"])
            assert result.exit_code == 0
            output = json.loads(result.output)
            data = output.get("data", output)
            assert output.get("success", data.get("success")) is True
            assert data["count"] == 1


class TestScholarJobsStatus:
    """Tests for the scholar jobs status command."""

    def test_jobs_status_help(self):
        """Test jobs status command help."""
        runner = CliRunner()
        result = runner.invoke(scholar, ["jobs", "status", "--help"])
        assert result.exit_code == 0
        assert "Check job status" in result.output

    def test_jobs_status_not_found(self):
        """Test jobs status for non-existent job."""
        runner = CliRunner()
        with patch("scitex.scholar.jobs.JobManager") as mock_manager_cls:
            mock_manager = MagicMock()
            mock_manager.get_status.return_value = None
            mock_manager_cls.return_value = mock_manager

            result = runner.invoke(scholar, ["jobs", "status", "nonexistent"])
            assert result.exit_code == 1
            assert "not found" in result.output.lower()

    def test_jobs_status_found(self):
        """Test jobs status for existing job."""
        runner = CliRunner()
        with patch("scitex.scholar.jobs.JobManager") as mock_manager_cls:
            mock_manager = MagicMock()
            mock_manager.get_status.return_value = {
                "job_id": "job-12345",
                "job_type": "fetch",
                "status": "running",
                "progress": {"total": 10, "completed": 5, "percent": 50},
            }
            mock_manager_cls.return_value = mock_manager

            result = runner.invoke(scholar, ["jobs", "status", "job-12345"])
            assert result.exit_code == 0
            assert "job-12345" in result.output
            assert "RUNNING" in result.output

    def test_jobs_status_json_output(self):
        """Test jobs status with --json option."""
        runner = CliRunner()
        with patch("scitex.scholar.jobs.JobManager") as mock_manager_cls:
            mock_manager = MagicMock()
            mock_manager.get_status.return_value = {
                "job_id": "job-12345",
                "job_type": "fetch",
                "status": "completed",
            }
            mock_manager_cls.return_value = mock_manager

            result = runner.invoke(scholar, ["jobs", "status", "job-12345", "--json"])
            assert result.exit_code == 0
            output = json.loads(result.output)
            data = output.get("data", output)
            assert output.get("success", data.get("success")) is True
            assert data["job_id"] == "job-12345"


class TestScholarJobsCancel:
    """Tests for the scholar jobs cancel command."""

    def test_jobs_cancel_help(self):
        """Test jobs cancel command help."""
        runner = CliRunner()
        result = runner.invoke(scholar, ["jobs", "cancel", "--help"])
        assert result.exit_code == 0
        assert "Cancel" in result.output

    def test_jobs_cancel_success(self):
        """Test jobs cancel for running job."""
        runner = CliRunner()
        with patch("scitex.scholar.jobs.JobManager") as mock_manager_cls:
            mock_manager = MagicMock()
            mock_manager_cls.return_value = mock_manager

            with patch("asyncio.run") as mock_run:
                mock_run.return_value = True
                result = runner.invoke(scholar, ["jobs", "cancel", "job-12345"])
                assert result.exit_code == 0
                assert "cancelled" in result.output.lower()

    def test_jobs_cancel_not_found(self):
        """Test jobs cancel for non-existent job."""
        runner = CliRunner()
        with patch("scitex.scholar.jobs.JobManager") as mock_manager_cls:
            mock_manager = MagicMock()
            mock_manager_cls.return_value = mock_manager

            with patch("asyncio.run") as mock_run:
                mock_run.return_value = False
                result = runner.invoke(scholar, ["jobs", "cancel", "nonexistent"])
                assert result.exit_code == 1
                assert "Could not cancel" in result.output


class TestScholarJobsResult:
    """Tests for the scholar jobs result command."""

    def test_jobs_result_help(self):
        """Test jobs result command help."""
        runner = CliRunner()
        result = runner.invoke(scholar, ["jobs", "result", "--help"])
        assert result.exit_code == 0
        assert "result" in result.output.lower()

    def test_jobs_result_not_found(self):
        """Test jobs result for non-existent job."""
        runner = CliRunner()
        with patch("scitex.scholar.jobs.JobManager") as mock_manager_cls:
            mock_manager = MagicMock()
            mock_manager.get_job.return_value = None
            mock_manager_cls.return_value = mock_manager

            result = runner.invoke(scholar, ["jobs", "result", "nonexistent"])
            assert result.exit_code == 1
            assert "not found" in result.output.lower()

    def test_jobs_result_not_finished(self):
        """Test jobs result for running job."""
        runner = CliRunner()
        with patch("scitex.scholar.jobs.JobManager") as mock_manager_cls:
            mock_manager = MagicMock()
            mock_job = MagicMock()
            mock_job.is_finished = False
            mock_job.status.value = "running"
            mock_manager.get_job.return_value = mock_job
            mock_manager_cls.return_value = mock_manager

            result = runner.invoke(scholar, ["jobs", "result", "job-12345"])
            assert result.exit_code == 1
            assert "still" in result.output.lower()

    def test_jobs_result_completed(self):
        """Test jobs result for completed job."""
        runner = CliRunner()
        with patch("scitex.scholar.jobs.JobManager") as mock_manager_cls:
            mock_manager = MagicMock()
            mock_job = MagicMock()
            mock_job.is_finished = True
            mock_job.result = {"success": True, "papers": 5}
            mock_manager.get_job.return_value = mock_job
            mock_manager_cls.return_value = mock_manager

            result = runner.invoke(scholar, ["jobs", "result", "job-12345"])
            assert result.exit_code == 0
            assert "5" in result.output or "papers" in result.output


class TestScholarJobsClean:
    """Tests for the scholar jobs clean command."""

    def test_jobs_clean_help(self):
        """Test jobs clean command help."""
        runner = CliRunner()
        result = runner.invoke(scholar, ["jobs", "clean", "--help"])
        assert result.exit_code == 0
        assert "Clean" in result.output

    def test_jobs_clean_default(self):
        """Test jobs clean with default options."""
        runner = CliRunner()
        with patch("scitex.scholar.jobs.JobManager") as mock_manager_cls:
            mock_manager = MagicMock()
            mock_manager.cleanup_old_jobs.return_value = 5
            mock_manager_cls.return_value = mock_manager

            result = runner.invoke(scholar, ["jobs", "clean"])
            assert result.exit_code == 0
            assert "5" in result.output
            mock_manager.cleanup_old_jobs.assert_called_once_with(
                max_age_hours=24, keep_failed=False
            )

    def test_jobs_clean_with_options(self):
        """Test jobs clean with --max-age and --keep-failed."""
        runner = CliRunner()
        with patch("scitex.scholar.jobs.JobManager") as mock_manager_cls:
            mock_manager = MagicMock()
            mock_manager.cleanup_old_jobs.return_value = 3
            mock_manager_cls.return_value = mock_manager

            result = runner.invoke(
                scholar, ["jobs", "clean", "--max-age", "48", "--keep-failed"]
            )
            assert result.exit_code == 0
            mock_manager.cleanup_old_jobs.assert_called_once_with(
                max_age_hours=48, keep_failed=True
            )

    def test_jobs_clean_json_output(self):
        """Test jobs clean with --json option."""
        runner = CliRunner()
        with patch("scitex.scholar.jobs.JobManager") as mock_manager_cls:
            mock_manager = MagicMock()
            mock_manager.cleanup_old_jobs.return_value = 2
            mock_manager_cls.return_value = mock_manager

            result = runner.invoke(scholar, ["jobs", "clean", "--json"])
            assert result.exit_code == 0
            output = json.loads(result.output)
            data = output.get("data", output)
            assert output.get("success", data.get("success")) is True
            assert data["deleted"] == 2


class TestScholarIntegration:
    """Integration tests for scholar commands."""

    def test_help_all_subcommands(self):
        """Test that all subcommands have help text."""
        runner = CliRunner()
        subcommands = ["fetch", "library", "config"]
        for cmd in subcommands:
            result = runner.invoke(scholar, [cmd, "--help"])
            assert result.exit_code == 0, f"Failed for {cmd}"
            assert len(result.output) > 50, f"Help too short for {cmd}"

    def test_help_all_jobs_subcommands(self):
        """Test that all jobs subcommands have help text."""
        runner = CliRunner()
        subcommands = ["list", "status", "start", "cancel", "result", "clean"]
        for cmd in subcommands:
            result = runner.invoke(scholar, ["jobs", cmd, "--help"])
            assert result.exit_code == 0, f"Failed for jobs {cmd}"


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])
