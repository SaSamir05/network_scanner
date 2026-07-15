"""Export scan results to CSV/JSON and persist history."""
from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Iterable, List

from scanner.device_info import Device

from .logger import get_logger

logger = get_logger(__name__)

HISTORY_DIR = Path(__file__).resolve().parent.parent / "data" / "history"
HISTORY_DIR.mkdir(parents=True, exist_ok=True)

_FIELDS = ["ip", "mac", "hostname", "vendor", "status"]


class Exporter:
    """Write scan results to disk."""

    @staticmethod
    def to_csv(devices: Iterable[Device], path: str | Path) -> Path:
        path = Path(path)
        with path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=_FIELDS)
            writer.writeheader()
            for dev in devices:
                row = {k: getattr(dev, k) for k in _FIELDS}
                writer.writerow(row)
        logger.info("Exported CSV: %s", path)
        return path

    @staticmethod
    def to_json(devices: Iterable[Device], path: str | Path) -> Path:
        path = Path(path)
        payload = [d.to_dict() for d in devices]
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        logger.info("Exported JSON: %s", path)
        return path

    @staticmethod
    def save_history(devices: List[Device]) -> Path:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = HISTORY_DIR / f"scan_{stamp}.json"
        return Exporter.to_json(devices, path)
