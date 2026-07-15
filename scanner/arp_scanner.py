"""ARP-based active device discovery using Scapy."""
from __future__ import annotations

from typing import List

from utils.logger import get_logger

from .device_info import Device

logger = get_logger(__name__)


class ARPScanner:
    """Discover devices via ARP requests on the local subnet.

    Requires elevated privileges (root/administrator) to send raw packets.
    """

    def __init__(self, timeout: int = 2, retry: int = 1) -> None:
        self.timeout = timeout
        self.retry = retry

    def scan(self, subnet: str) -> List[Device]:
        """Broadcast an ARP request across ``subnet`` (CIDR) and return devices."""
        try:
            from scapy.all import ARP, Ether, srp  # type: ignore
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("Scapy is required for ARP scanning") from exc

        logger.info("ARP scan starting on %s", subnet)
        arp = ARP(pdst=subnet)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether / arp

        try:
            answered, _ = srp(
                packet, timeout=self.timeout, retry=self.retry, verbose=False
            )
        except PermissionError as exc:
            raise PermissionError(
                "ARP scan requires administrator/root privileges."
            ) from exc
        except OSError as exc:
            raise PermissionError(
                f"Unable to open raw socket for ARP scan: {exc}"
            ) from exc

        devices: List[Device] = []
        for _, received in answered:
            devices.append(
                Device(
                    ip=received.psrc,
                    mac=received.hwsrc.lower(),
                    status="Active",
                )
            )
        logger.info("ARP scan complete: %d devices", len(devices))
        return devices
