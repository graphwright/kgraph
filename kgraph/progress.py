"""Progress tracking for long-running pipeline operations."""

import sys
import time

from pydantic import BaseModel, Field


class ProgressTracker(BaseModel):
    """Track and report progress during long-running operations."""

    total: int
    completed: int = 0
    report_interval: float = 30.0
    start_time: float = Field(default_factory=time.time)
    last_report_time: float = Field(default_factory=time.time)

    def increment(self) -> None:
        """Increment completed count and report if interval elapsed."""
        self.completed += 1
        now = time.time()
        if (now - self.last_report_time) >= self.report_interval:
            self.report()
            self.last_report_time = now

    def report(self) -> None:
        """Print progress report to stderr."""
        elapsed = time.time() - self.start_time
        pct = (100.0 * self.completed / self.total) if self.total else 0.0
        parts = [f"Progress: {self.completed}/{self.total} ({pct:.1f}%)"]
        if elapsed > 0:
            rate = self.completed / elapsed
            parts.append(f" {rate:.1f} papers/sec")
        parts.append(f" Elapsed: {elapsed / 60:.1f} min")
        if self.completed < self.total and self.completed > 0 and elapsed > 0:
            remaining = (elapsed / self.completed) * (self.total - self.completed)
            parts.append(f" ~{remaining / 60:.1f} min remaining")
        print("".join(parts), file=sys.stderr)
