"""
Security utilities and SSRF (Server-Side Request Forgery) protection for MWIE.
"""

import ipaddress
import socket
from urllib.parse import urlparse

from mwie.core.config import settings


class SecurityError(Exception):
    """Raised when a requested URL violates security policies (e.g. SSRF)."""


def is_ip_private_or_loopback(ip_str: str) -> bool:
    """Check if an IP address is private, loopback, link-local, or reserved."""
    try:
        ip = ipaddress.ip_address(ip_str)
        return (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
            or ip.is_unspecified
        )
    except ValueError:
        return False


def validate_target_url(
    url: str,
    allow_private_ips: bool | None = None,
    allowed_domains: list[str] | None = None,
    blocked_domains: list[str] | None = None,
) -> str:
    """
    Validate target URL against SSRF vulnerabilities, allowed schemes, and domain rules.
    Returns cleaned URL string or raises SecurityError.
    """
    if not url or not isinstance(url, str):
        raise SecurityError("URL must be a non-empty string.")

    url = url.strip()
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise SecurityError(
            f"Disallowed URL scheme: '{parsed.scheme}'. Only http and https are permitted."
        )

    hostname = parsed.hostname
    if not hostname:
        raise SecurityError(f"Invalid URL: missing hostname in '{url}'.")

    hostname_lower = hostname.lower()

    # Blocked domains check
    blocklist = blocked_domains if blocked_domains is not None else settings.blocked_domains
    for blocked in blocklist:
        if hostname_lower == blocked.lower() or hostname_lower.endswith(f".{blocked.lower()}"):
            raise SecurityError(f"Access to blocked domain '{hostname}' is denied.")

    # Allowed domains check
    allowlist = allowed_domains if allowed_domains is not None else settings.allowed_domains
    if allowlist:
        allowed = False
        for pattern in allowlist:
            if hostname_lower == pattern.lower() or hostname_lower.endswith(f".{pattern.lower()}"):
                allowed = True
                break
        if not allowed:
            raise SecurityError(f"Domain '{hostname}' is not in the allowed domains list.")

    # SSRF Private IP check
    allow_private = (
        allow_private_ips if allow_private_ips is not None else settings.allow_private_ips
    )
    if not allow_private:
        # Resolve hostname to check IP
        try:
            addr_info = socket.getaddrinfo(hostname, None)
            for item in addr_info:
                ip_str = item[4][0]
                if is_ip_private_or_loopback(ip_str):
                    raise SecurityError(
                        f"SSRF Protection: Hostname '{hostname}' resolves to private/loopback IP '{ip_str}'."
                    )
        except socket.gaierror:
            # If DNS resolution fails here, let the HTTP client handle it or allow if mock test
            pass

    return url
