"""Tests for ProgressTracker (kgraph.progress).

Tests progress tracking and reporting functionality.
"""

import time
from io import StringIO
from unittest.mock import patch

from kgraph.progress import ProgressTracker


class TestProgressTrackerBasics:
    """Test basic ProgressTracker functionality."""

    def test_initial_state(self):
        """Tracker should start with zero completed."""
        tracker = ProgressTracker(total=10)
        assert tracker.total == 10
        assert tracker.completed == 0

    def test_increment_increases_completed(self):
        """Increment should increase completed count."""
        tracker = ProgressTracker(total=10, report_interval=9999)  # Large interval to prevent auto-report
        tracker.increment()
        assert tracker.completed == 1
        tracker.increment()
        assert tracker.completed == 2

    def test_percentage_calculation(self):
        """Report should calculate correct percentage."""
        tracker = ProgressTracker(total=100, report_interval=9999)
        tracker.completed = 25

        with patch("sys.stderr", new=StringIO()) as mock_stdout:
            tracker.report()
            output = mock_stdout.getvalue()

        assert "25.0%" in output

    def test_percentage_zero_total(self):
        """Report should handle zero total gracefully."""
        tracker = ProgressTracker(total=0, report_interval=9999)

        with patch("sys.stderr", new=StringIO()) as mock_stdout:
            tracker.report()
            output = mock_stdout.getvalue()

        assert "0.0%" in output

    def test_report_shows_progress_count(self):
        """Report should show completed/total count."""
        tracker = ProgressTracker(total=50, report_interval=9999)
        tracker.completed = 25

        with patch("sys.stderr", new=StringIO()) as mock_stdout:
            tracker.report()
            output = mock_stdout.getvalue()

        assert "25/50" in output


class TestProgressTrackerTiming:
    """Test ProgressTracker timing-related functionality."""

    def test_rate_calculation(self):
        """Report should calculate processing rate."""
        tracker = ProgressTracker(total=100, report_interval=9999)
        tracker.completed = 10
        # Simulate 10 seconds elapsed
        tracker.start_time = time.time() - 10.0

        with patch("sys.stderr", new=StringIO()) as mock_stdout:
            tracker.report()
            output = mock_stdout.getvalue()

        # Rate should be ~1.0 papers/sec (10 completed in 10 seconds)
        assert "papers/sec" in output

    def test_elapsed_time_shown(self):
        """Report should show elapsed time."""
        tracker = ProgressTracker(total=100, report_interval=9999)
        tracker.completed = 50
        # Simulate 2 minutes elapsed
        tracker.start_time = time.time() - 120.0

        with patch("sys.stderr", new=StringIO()) as mock_stdout:
            tracker.report()
            output = mock_stdout.getvalue()

        assert "Elapsed:" in output
        assert "min" in output

    def test_estimated_remaining_shown(self):
        """Report should show estimated remaining time when not complete."""
        tracker = ProgressTracker(total=100, report_interval=9999)
        tracker.completed = 50
        # Simulate 1 minute elapsed (should estimate 1 more minute)
        tracker.start_time = time.time() - 60.0

        with patch("sys.stderr", new=StringIO()) as mock_stdout:
            tracker.report()
            output = mock_stdout.getvalue()

        assert "remaining" in output.lower()


class TestProgressTrackerAutoReport:
    """Test automatic reporting based on interval."""

    def test_no_auto_report_before_interval(self):
        """Should not auto-report before interval elapses."""
        tracker = ProgressTracker(total=10, report_interval=9999)

        with patch("sys.stderr", new=StringIO()) as mock_stdout:
            tracker.increment()
            output = mock_stdout.getvalue()

        # No report should be printed
        assert "Progress:" not in output

    def test_auto_report_after_interval(self):
        """Should auto-report when interval elapses."""
        tracker = ProgressTracker(total=10, report_interval=0.001)  # Very short interval
        # Simulate time passing
        tracker.last_report_time = time.time() - 1.0  # 1 second ago

        with patch("sys.stderr", new=StringIO()) as mock_stdout:
            tracker.increment()
            output = mock_stdout.getvalue()

        assert "Progress:" in output


class TestProgressTrackerEdgeCases:
    """Test edge cases for ProgressTracker."""

    def test_large_total(self):
        """Should handle large totals."""
        tracker = ProgressTracker(total=1_000_000, report_interval=9999)
        tracker.completed = 500_000

        with patch("sys.stderr", new=StringIO()) as mock_stdout:
            tracker.report()
            output = mock_stdout.getvalue()

        assert "50.0%" in output

    def test_custom_report_interval(self):
        """Should respect custom report interval."""
        tracker = ProgressTracker(total=10, report_interval=60.0)
        assert tracker.report_interval == 60.0

    def test_completed_equals_total(self):
        """Should handle 100% completion."""
        tracker = ProgressTracker(total=10, report_interval=9999)
        tracker.completed = 10

        with patch("sys.stderr", new=StringIO()) as mock_stdout:
            tracker.report()
            output = mock_stdout.getvalue()

        assert "100.0%" in output
