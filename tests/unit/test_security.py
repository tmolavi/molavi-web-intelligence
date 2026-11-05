import pytest

from mwie.core.security import (
    SecurityError,
    is_ip_private_or_loopback,
    validate_target_url,
)


def test_private_ip_detection():
    assert is_ip_private_or_loopback("127.0.0.1") is True
    assert is_ip_private_or_loopback("10.0.0.1") is True
    assert is_ip_private_or_loopback("192.168.1.1") is True
    assert is_ip_private_or_loopback("172.16.0.1") is True
    assert is_ip_private_or_loopback("8.8.8.8") is False


def test_validate_target_url_ssrf():
    # Loopback domain
    with pytest.raises(SecurityError):
        validate_target_url("http://localhost:8000")

    with pytest.raises(SecurityError):
        validate_target_url("http://127.0.0.1/admin")

    # Invalid scheme
    with pytest.raises(SecurityError):
        validate_target_url("file:///etc/passwd")

    with pytest.raises(SecurityError):
        validate_target_url("gopher://evil.com")

    # Valid public url
    valid = validate_target_url("https://molavi.pro/blog")
    assert valid == "https://molavi.pro/blog"


def test_domain_allowlist():
    with pytest.raises(SecurityError):
        validate_target_url("https://untrusted.com", allowed_domains=["molavi.pro"])

    valid = validate_target_url("https://sub.molavi.pro/test", allowed_domains=["molavi.pro"])
    assert "sub.molavi.pro" in valid
