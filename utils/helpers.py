"""Networking helpers: subnet detection, gateway, local host info."""
from __future__ import annotations

import ipaddress
import platform
import socket
import subprocess
from dataclasses import dataclass
from typing import Optional

from .logger import get_logger

logger = get_logger(__name__)


@dataclass
class LocalHostInfo:
    """Information about the local machine."""

    hostname: str
    ip_address: str
    subnet_cidr: str
    gateway: Optional[str]
    system: str


def get_local_ip() -> str:
    """Best-effort discovery of the primary outbound IPv4 address."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Does not actually send packets; used to pick the outbound iface.
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        sock.close()


def get_default_gateway() -> Optional[str]:
    """Return the default IPv4 gateway or None if not detectable."""
    system = platform.system().lower()
    try:
        if system == "windows":
            out = subprocess.check_output(
                ["ipconfig"], text=True, stderr=subprocess.DEVNULL
            )
            for line in out.splitlines():
                if "Default Gateway" in line:
                    parts = line.split(":")
                    if len(parts) >= 2:
                        gw = parts[1].strip()
                        if gw and gw != "::":
                            return gw
        else:
            # Linux / macOS
            try:
                out = subprocess.check_output(
                    ["ip", "route"], text=True, stderr=subprocess.DEVNULL
                )
                for line in out.splitlines():
                    if line.startswith("default"):
                        return line.split()[2]
            except (FileNotFoundError, subprocess.CalledProcessError):
                out = subprocess.check_output(
                    ["netstat", "-rn"], text=True, stderr=subprocess.DEVNULL
                )
                for line in out.splitlines():
                    if line.startswith("default") or line.startswith("0.0.0.0"):
                        parts = line.split()
                        if len(parts) >= 2:
                            return parts[1]
    except Exception as exc:  # pragma: no cover - platform dependent
        logger.warning("Gateway detection failed: %s", exc)
    return None


def detect_subnet(ip: str, prefix: int = 24) -> str:
    """Return CIDR subnet for the given IP, defaulting to /24."""
    network = ipaddress.ip_network(f"{ip}/{prefix}", strict=False)
    return str(network)


def get_local_host_info() -> LocalHostInfo:
    """Gather local machine networking information."""
    ip = get_local_ip()
    return LocalHostInfo(
        hostname=socket.gethostname(),
        ip_address=ip,
        subnet_cidr=detect_subnet(ip),
        gateway=get_default_gateway(),
        system=platform.system(),
    )


def ping_host(ip: str, timeout: int = 1) -> bool:
    """Ping a host once; return True if reachable."""
    system = platform.system().lower()
    count_flag = "-n" if system == "windows" else "-c"
    timeout_flag = "-w" if system == "windows" else "-W"
    timeout_val = str(timeout * 1000) if system == "windows" else str(timeout)
    try:
        result = subprocess.run(
            ["ping", count_flag, "1", timeout_flag, timeout_val, ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=timeout + 2,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False
