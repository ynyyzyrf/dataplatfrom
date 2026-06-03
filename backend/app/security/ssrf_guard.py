"""SSRF (Server-Side Request Forgery) protection helpers.

Blocks requests to private / internal IP ranges and cloud metadata
endpoints by default.
"""

from __future__ import annotations

import ipaddress
from typing import Final

from app.config import settings

# Cloud metadata IPs (AWS, GCP, Azure)
_METADATA_CIDRS: Final[list[str]] = [
    "169.254.169.254/32",  # AWS
    "169.254.0.0/16",      # GCP
    "168.63.129.16/32",    # Azure
]

_BLOCKED_RANGES: Final[list[ipaddress.IPv4Network]] = [
    ipaddress.ip_network(cidr) for cidr in [
        "0.0.0.0/8",
        "10.0.0.0/8",
        "100.64.0.0/10",
        "127.0.0.0/8",
        "169.254.0.0/16",
        "172.16.0.0/12",
        "192.0.0.0/24",
        "192.0.2.0/24",
        "192.168.0.0/16",
        "198.18.0.0/15",
        "198.51.100.0/24",
        "203.0.113.0/24",
        "224.0.0.0/4",
        "240.0.0.0/4",
        "255.255.255.255/32",
    ]
    + [ipaddress.ip_network(cidr) for cidr in _METADATA_CIDRS]
)


def _is_blocked_address(addr: str) -> bool:
    """Check if *addr* resolves to a blocked IP range."""
    try:
        parsed = ipaddress.ip_address(addr)
    except ValueError:
        return True  # Cannot resolve → block

    if settings.ssrf_block_private_ranges:
        for net in _BLOCKED_RANGES:
            if parsed in net:
                return True
    return False


async def resolve_and_check(url: str) -> str:
    """Resolve the URL hostname, check its IP, and return the resolved IP.

    Raises ``ValueError`` if the address is blocked.
    """
    # Simple hostname extraction (not full URL parsing, but sufficient for guard)
    from urllib.parse import urlparse

    parsed = urlparse(url)
    hostname = parsed.hostname or parsed.netloc

    import asyncio

    try:
        answers = await asyncio.get_running_loop().run_in_executor(
            None, _resolve_ips, hostname
        )
    except Exception:
        raise ValueError(f"Cannot resolve hostname: {hostname}")

    if settings.ssrf_block_private_ranges:
        for ip_str in answers:
            if _is_blocked_address(ip_str):
                raise ValueError(f"SSRF protection: blocked host {hostname} -> {ip_str}")

    # Also check the hostname itself against an allow-list if configured
    if settings.ssrf_allow_list and hostname not in settings.ssrf_allow_list:
        raise ValueError(f"SSRF protection: host {hostname} not in allow-list")

    return answers[0] if answers else ""


def _resolve_ips(hostname: str) -> list[str]:
    """Synchronous DNS resolution."""
    import socket

    results: list[str] = []
    try:
        for info in socket.getaddrinfo(hostname, None):
            results.append(info[4][0])
    except socket.gaierror:
        pass
    return results
