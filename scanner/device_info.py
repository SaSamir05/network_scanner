"""Device data model and enrichment helpers."""
from __future__ import annotations

import socket
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Optional

try:
    from mac_vendor_lookup import MacLookup, VendorNotFoundError
    _MAC_LOOKUP: Optional[MacLookup] = MacLookup()
except Exception:  # pragma: no cover - offline fallback
    _MAC_LOOKUP = None

    class VendorNotFoundError(Exception):
        pass


@dataclass
class Device:
    """Represents a discovered device on the network."""

    ip: str
    mac: str
    hostname: str = "Unknown"
    vendor: str = "Unknown"
    status: str = "Active"
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Return a plain dict representation (for JSON/CSV)."""
        return asdict(self)


def resolve_hostname(ip: str, timeout: float = 0.5) -> str:
    """Reverse-DNS lookup with short timeout."""
    old = socket.getdefaulttimeout()
    socket.setdefaulttimeout(timeout)
    try:
        return socket.gethostbyaddr(ip)[0]
    except (socket.herror, socket.gaierror, OSError):
        return "Unknown"
    finally:
        socket.setdefaulttimeout(old)


def resolve_vendor(mac: str) -> str:
    """Lookup vendor from OUI prefix."""
    if not _MAC_LOOKUP or not mac:
        return "Unknown"
    try:
        return _MAC_LOOKUP.lookup(mac)
    except (VendorNotFoundError, Exception):
        return "Unknown"
