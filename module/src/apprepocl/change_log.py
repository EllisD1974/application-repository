from dataclasses import dataclass
from collections import defaultdict
from typing import List


@dataclass
class Log:
    version: str
    description: str
    ticket: str = None
    visible: bool = True

    def __str__(self) -> str:
        prefix = f"[{self.ticket}] " if self.ticket else ""
        return f"{prefix}{self.description}"


class Changelog:
    def __init__(self, logs: List[Log] = None):
        self._logs = logs or []

    def add_log(self, log: Log) -> None:
        """Add a new log entry."""
        self._logs.append(log)

    def get_logs_for_version(self, version: str) -> List[Log]:
        """Get list of all logs for given version."""
        return [log for log in self._logs if log.version == version]

    def get_all_logs(self) -> List[Log]:
        """Get flattened list of all logs for all versions."""
        return list(self._logs)

    def __str__(self):
        parts = []
        versions = sorted({log.version for log in self._logs})
        for version in versions:
            parts.append(f"Version {version}")
            for log in self.get_logs_for_version(version):
                parts.append(f"{log}")
        return "\n".join(parts)


if __name__ == "__main__":
    change_log = Changelog()

    pause = 1
