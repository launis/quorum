"""Unit tests for MCPUrlValidator SSRF and DNS-rebinding egress firewall."""

import socket
from typing import Never

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.services.mcp.url_validator import MCPUrlValidator


def _fake_addrinfo(*ips: str) -> list[tuple[socket.AddressFamily, socket.SocketKind, int, str, tuple[str, int]]]:
    """Build synthetic socket.getaddrinfo tuples for deterministic DNS testing.

    Args:
        *ips: IP address strings to include in the mocked DNS response.

    Returns:
        List of synthetic addrinfo tuples.
    """
    records: list[tuple[socket.AddressFamily, socket.SocketKind, int, str, tuple[str, int]]] = []
    for ip in ips:
        family = socket.AF_INET6 if ":" in ip else socket.AF_INET
        records.append((family, socket.SOCK_STREAM, 6, "", (ip, 443)))
    return records


def test_validate_mcp_endpoint_url_accepts_public_https_and_http(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify public IPv4 and IPv6 DNS records pass egress validation.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
    """
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda host, port, type=0: _fake_addrinfo("93.184.216.34", "2606:2800:220:1:248:1893:25c8:1946"),
    )

    https_result = MCPUrlValidator.validate_mcp_endpoint_url("  https://mcp.example.com/v1/mcp  ")
    assert https_result == "https://mcp.example.com/v1/mcp"

    http_result = MCPUrlValidator.validate_mcp_endpoint_url("http://mcp.example.com:8080/sse")
    assert http_result == "http://mcp.example.com:8080/sse"


@pytest.mark.parametrize(
    "invalid_url",
    [
        "",
        "   ",
        "file:///etc/passwd",
        "gopher://example.com:70/1",
        "ws://mcp.example.com/socket",
        "wss://mcp.example.com/socket",
        "ftp://mcp.example.com/resource",
        "https:///missing-host",
        "https://user:secret@mcp.example.com/mcp",
        "https://mcp.example.com:99999/mcp",
        "https://mcp.example.com:notaport/mcp",
    ],
)
def test_validate_mcp_endpoint_url_rejects_invalid_schemes_ports_and_credentials(invalid_url: str) -> None:
    """Verify disallowed URL schemes, missing hostnames, embedded credentials, and invalid ports fail fast.

    Args:
        invalid_url: Malformed or prohibited URL string under test.
    """
    with pytest.raises(AppException) as exc_info:
        MCPUrlValidator.validate_mcp_endpoint_url(invalid_url)

    assert exc_info.value.status_code == 403
    assert exc_info.value.details["error_code"] == ErrorCodes.SECURITY_VIOLATION.value


@pytest.mark.parametrize("allow_private", [False, True])
@pytest.mark.parametrize(
    "metadata_url",
    [
        "http://169.254.169.254/latest/meta-data/",
        "http://metadata.google.internal/computeMetadata/v1/",
        "http://sub.metadata.google.internal/computeMetadata/v1/",
        "http://metadata/computeMetadata/v1/",
        "http://[fd00:ec2::254]/latest/meta-data/",
    ],
)
def test_validate_mcp_endpoint_url_unconditionally_blocks_cloud_metadata_hosts(
    metadata_url: str,
    allow_private: bool,
) -> None:
    """Verify cloud instance metadata endpoints are blocked even when private networks are allowed.

    Args:
        metadata_url: Cloud metadata URL under test.
        allow_private: Flag controlling private network permission.
    """
    with pytest.raises(AppException) as exc_info:
        MCPUrlValidator.validate_mcp_endpoint_url(metadata_url, allow_private_networks=allow_private)

    assert exc_info.value.status_code == 403
    assert exc_info.value.details["error_code"] == ErrorCodes.SECURITY_VIOLATION.value


@pytest.mark.parametrize("allow_private", [False, True])
@pytest.mark.parametrize(
    "resolved_ip",
    [
        "169.254.169.254",
        "fd00:ec2::254",
        "::ffff:169.254.169.254",
        "0.0.0.0",
        "::",
        "224.0.0.1",
    ],
)
def test_validate_mcp_endpoint_url_unconditionally_blocks_metadata_unspecified_and_multicast_ips(
    monkeypatch: pytest.MonkeyPatch,
    resolved_ip: str,
    allow_private: bool,
) -> None:
    """Verify DNS records resolving to cloud metadata, unspecified, or multicast IPs are always blocked.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
        resolved_ip: Synthetic resolved IP address.
        allow_private: Flag controlling private network permission.
    """
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda host, port, type=0: _fake_addrinfo(resolved_ip),
    )

    with pytest.raises(AppException) as exc_info:
        MCPUrlValidator.validate_mcp_endpoint_url(
            "https://rebind.example.com/mcp",
            allow_private_networks=allow_private,
        )

    assert exc_info.value.status_code == 403
    assert exc_info.value.details["error_code"] == ErrorCodes.SECURITY_VIOLATION.value


@pytest.mark.parametrize(
    "loopback_url",
    [
        "http://localhost:8080/mcp",
        "http://localhost.localdomain:8080/mcp",
        "http://service.localhost:8080/mcp",
    ],
)
def test_validate_mcp_endpoint_url_blocks_loopback_hostnames_by_default_and_allows_when_enabled(
    monkeypatch: pytest.MonkeyPatch,
    loopback_url: str,
) -> None:
    """Verify loopback hostnames are rejected when allow_private_networks is False and allowed when True.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
        loopback_url: Loopback URL under test.
    """
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda host, port, type=0: _fake_addrinfo("127.0.0.1"),
    )

    with pytest.raises(AppException) as exc_info:
        MCPUrlValidator.validate_mcp_endpoint_url(loopback_url, allow_private_networks=False)
    assert exc_info.value.details["error_code"] == ErrorCodes.SECURITY_VIOLATION.value

    validated = MCPUrlValidator.validate_mcp_endpoint_url(loopback_url, allow_private_networks=True)
    assert validated == loopback_url


@pytest.mark.parametrize(
    "private_ip",
    [
        "127.0.0.1",
        "::1",
        "::ffff:127.0.0.1",
        "10.0.0.42",
        "172.16.5.10",
        "172.31.255.254",
        "192.168.1.100",
        "169.254.10.20",
        "fc00::1234",
        "fe80::1%eth0",
    ],
)
def test_validate_mcp_endpoint_url_blocks_private_and_loopback_ips_unless_allowed(
    monkeypatch: pytest.MonkeyPatch,
    private_ip: str,
) -> None:
    """Verify private CIDR, link-local, and loopback IPs are blocked unless allow_private_networks=True.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
        private_ip: Private or loopback IP string under test.
    """
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda host, port, type=0: _fake_addrinfo(private_ip),
    )

    with pytest.raises(AppException) as exc_info:
        MCPUrlValidator.validate_mcp_endpoint_url(
            "https://internal.example.com/mcp",
            allow_private_networks=False,
        )
    assert exc_info.value.details["error_code"] == ErrorCodes.SECURITY_VIOLATION.value

    validated = MCPUrlValidator.validate_mcp_endpoint_url(
        "https://internal.example.com/mcp",
        allow_private_networks=True,
    )
    assert validated == "https://internal.example.com/mcp"


def test_validate_mcp_endpoint_url_blocks_dns_rebinding_mixed_records(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify a hostname returning both a public IP and a private IP is blocked against DNS rebinding.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
    """
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda host, port, type=0: _fake_addrinfo("93.184.216.34", "10.240.0.5"),
    )

    with pytest.raises(AppException) as exc_info:
        MCPUrlValidator.validate_mcp_endpoint_url("https://rebind.example.com/mcp", allow_private_networks=False)

    assert exc_info.value.status_code == 403
    assert exc_info.value.details["error_code"] == ErrorCodes.SECURITY_VIOLATION.value


def test_validate_mcp_endpoint_url_handles_dns_resolution_failures(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify socket.gaierror, empty DNS results, and malformed IP records raise SECURITY_VIOLATION.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
    """

    def _raise_gaierror(host: str, port: int, type: int = 0) -> Never:
        raise socket.gaierror("Name or service not known")

    monkeypatch.setattr(socket, "getaddrinfo", _raise_gaierror)
    with pytest.raises(AppException) as exc_info:
        MCPUrlValidator.validate_mcp_endpoint_url("https://nonexistent.example.com/mcp")
    assert exc_info.value.details["error_code"] == ErrorCodes.SECURITY_VIOLATION.value

    monkeypatch.setattr(socket, "getaddrinfo", lambda host, port, type=0: [])
    with pytest.raises(AppException) as empty_exc:
        MCPUrlValidator.validate_mcp_endpoint_url("https://empty.example.com/mcp")
    assert empty_exc.value.details["error_code"] == ErrorCodes.SECURITY_VIOLATION.value

    monkeypatch.setattr(socket, "getaddrinfo", lambda host, port, type=0: _fake_addrinfo("not-an-ip"))
    with pytest.raises(AppException) as invalid_ip_exc:
        MCPUrlValidator.validate_mcp_endpoint_url("https://corrupt.example.com/mcp")
    assert invalid_ip_exc.value.details["error_code"] == ErrorCodes.SECURITY_VIOLATION.value
