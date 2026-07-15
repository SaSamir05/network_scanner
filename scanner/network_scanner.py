"""High-level orchestrator: ARP scan + enrichment + threading."""
from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Callable, List, Optional

from utils.helpers import LocalHostInfo, get_local_host_info
from utils.logger import get_logger

from .arp_scanner import ARPScanner
from .device_info import Device, resolve_hostname, resolve_vendor

logger = get_logger(__name__)


@dataclass
class ScanResult:
    """Container for a completed scan."""

    devices: List[Device] = field(default_factory=list)
    duration_seconds: float = 0.0
    subnet: str = ""
    host: Optional[LocalHostInfo] = None
    error: Optional[str] = None

    @property
    def total(self) -> int:
        return len(self.devices)


class NetworkScanner:
    """Coordinates ARP scanning and parallel enrichment."""

    def __init__(self, max_workers: int = 32) -> None:
        self.max_workers = max_workers
        self._arp = ARPScanner()

    def scan(
        self,
        subnet: Optional[str] = None,
        progress_cb: Optional[Callable[[float, str], None]] = None,
    ) -> ScanResult:
        """Perform a full scan and return :class:`ScanResult`.

        ``progress_cb`` receives ``(percent 0-1, message)`` updates.
        """
        started = time.perf_counter()
        host = get_local_host_info()
        target = subnet or host.subnet_cidr
        logger.info("Scanning subnet %s (local=%s gw=%s)",
                    target, host.ip_address, host.gateway)

        if progress_cb:
            progress_cb(0.05, f"Discovering hosts on {target}...")

        try:
            devices = self._arp.scan(target)
        except PermissionError as exc:
            logger.error("Permission error: %s", exc)
            return ScanResult(
                devices=[], duration_seconds=time.perf_counter() - started,
                subnet=target, host=host, error=str(exc),
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception("Scan failed")
            return ScanResult(
                devices=[], duration_seconds=time.perf_counter() - started,
                subnet=target, host=host, error=str(exc),
            )

        if progress_cb:
            progress_cb(0.4, f"Enriching {len(devices)} devices...")

        self._enrich(devices, progress_cb)

        # Flag the gateway visibly.
        for device in devices:
            if host.gateway and device.ip == host.gateway:
                device.extra["role"] = "gateway"

        duration = time.perf_counter() - started
        if progress_cb:
            progress_cb(1.0, f"Done in {duration:.2f}s")
        return ScanResult(
            devices=sorted(devices, key=lambda d: tuple(int(p) for p in d.ip.split("."))),
            duration_seconds=duration, subnet=target, host=host,
        )

    def _enrich(
        self,
        devices: List[Device],
        progress_cb: Optional[Callable[[float, str], None]],
    ) -> None:
        if not devices:
            return
        total = len(devices)
        done = 0

        def _worker(dev: Device) -> Device:
            dev.hostname = resolve_hostname(dev.ip)
            dev.vendor = resolve_vendor(dev.mac)
            return dev

        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            futures = [pool.submit(_worker, d) for d in devices]
            for _ in as_completed(futures):
                done += 1
                if progress_cb:
                    pct = 0.4 + 0.6 * (done / total)
                    progress_cb(pct, f"Resolved {done}/{total}")
