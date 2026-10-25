"""SSRF and DNS-rebinding network egress firewall for outbound MCP endpoints."""

import ipaddress
import logging
import socket
from urllib.parse import ParseResult, urlparse

from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)

_ALLOWED_SCHEMES: frozenset[str] = frozenset({"http", "https"})
_CLOUD_METADATA_HOSTNAMES: frozenset[str] = frozenset(
    {
        "metadata.google.internal",
        "metadata",
        "169.254.169.254",
        "fd00:ec2::254",
    }
)
_CLOUD_METADATA_IPS: frozenset[ipaddress.IPv4Address | ipaddress.IPv6Address] = frozenset(
    {
        ipaddress.ip_address("169.254.169.254"),
        ipaddress.ip_address("fd00:ec2::254"),
    }
)
_LOOPBACK_HOSTNAMES: frozenset[str] = frozenset({"localhost", "localhost.localdomain"})


class MCPUrlValidator:
    """Validates outbound MCP server URLs against SSRF, cloud metadata, and private CIDR ranges."""

    @classmethod
    def validate_mcp_endpoint_url(
        cls,
        url: str,
        *,
        allow_private_networks: bool = False,
    ) -> str:
        """Validate an MCP endpoint URL and all resolved DNS A/AAAA records.

        # Phase 2, Step 2.1: SSRF URL & Network Egress Validator

        Args:
            url: Target MCP server URL to validate.
            allow_private_networks: Whether loopback and RFC-1918 private networks are permitted.

        Returns:
            Normalized validated URL string.

        Raises:
            AppException: With ErrorCodes.SECURITY_VIOLATION if scheme, hostname, or resolved IP is prohibited.
        """
        normalized_url = url.strip()
        if not normalized_url:
            raise cls._build_security_violation("MCP endpoint URL must not be empty.", url=url)

        parsed = urlparse(normalized_url)
        scheme = parsed.scheme.lower()
        if scheme not in _ALLOWED_SCHEMES:
            raise cls._build_security_violation(
                f"Disallowed URL scheme '{parsed.scheme}' for MCP endpoint.",
                url=normalized_url,
            )

        if parsed.username is not None or parsed.password is not None:
            raise cls._build_security_violation(
                "Embedded credentials in MCP endpoint URL are prohibited.",
                url=normalized_url,
            )

        hostname = parsed.hostname
        if hostname is None or not hostname.strip():
            raise cls._build_security_violation("MCP endpoint URL is missing a valid hostname.", url=normalized_url)

        clean_host = hostname.strip().lower().rstrip(".")
        cls._validate_hostname_tokens(
            clean_host=clean_host,
            url=normalized_url,
            allow_private_networks=allow_private_networks,
        )

        port = cls._resolve_port(parsed=parsed, scheme=scheme, url=normalized_url)
        resolved_ips = cls._resolve_all_ip_addresses(hostname=clean_host, port=port, url=normalized_url)

        for ip_addr in resolved_ips:
            cls._validate_ip_address(
                ip_addr=ip_addr,
                url=normalized_url,
                allow_private_networks=allow_private_networks,
            )

        return normalized_url

    @classmethod
    def _validate_hostname_tokens(
        cls,
        *,
        clean_host: str,
        url: str,
        allow_private_networks: bool,
    ) -> None:
        """Check hostname against cloud metadata and loopback hostnames before DNS resolution.

        Args:
            clean_host: Lowercase normalized hostname.
            url: Original endpoint URL for structured error context.
            allow_private_networks: Whether loopback networks are allowed.

        Raises:
            AppException: With ErrorCodes.SECURITY_VIOLATION if the hostname is prohibited.
        """
        if clean_host in _CLOUD_METADATA_HOSTNAMES or clean_host.endswith(".metadata.google.internal"):
            raise cls._build_security_violation(
                "Access to cloud instance metadata endpoints is strictly prohibited.",
                url=url,
            )

        if not allow_private_networks and (clean_host in _LOOPBACK_HOSTNAMES or clean_host.endswith(".localhost")):
            raise cls._build_security_violation(
                "Loopback hostnames are prohibited when allow_private_networks is False.",
                url=url,
            )

    @classmethod
    def _resolve_port(cls, *, parsed: ParseResult, scheme: str, url: str) -> int:
        """Resolve explicit or scheme-default TCP port for DNS resolution.

        Args:
            parsed: Parsed URL result from urlparse.
            scheme: Validated URL scheme ('http' or 'https').
            url: Endpoint URL for structured error logging.

        Returns:
            Resolved TCP port integer.

        Raises:
            AppException: With ErrorCodes.SECURITY_VIOLATION if port parsing fails or is out of bounds.
        """
        try:
            port_value = parsed.port
        except ValueError as exc:
            raise cls._build_security_violation("Invalid port in MCP endpoint URL.", url=url) from exc

        if port_value is not None:
            return port_value

        if scheme == "https":
            return 443
        return 80

    @classmethod
    def _resolve_all_ip_addresses(
        cls,
        *,
        hostname: str,
        port: int,
        url: str,
    ) -> list[ipaddress.IPv4Address | ipaddress.IPv6Address]:
        """Resolve all A and AAAA records for hostname via socket.getaddrinfo.

        Args:
            hostname: Target hostname or IP literal.
            port: Target TCP port.
            url: Endpoint URL for structured error context.

        Returns:
            Deduplicated list of resolved IPv4Address and IPv6Address objects.

        Raises:
            AppException: With ErrorCodes.SECURITY_VIOLATION if DNS resolution fails or yields no records.
        """
        try:
            addr_info_list = socket.getaddrinfo(hostname, port, type=socket.SOCK_STREAM)
        except (socket.gaierror, UnicodeError, OSError) as exc:
            raise cls._build_security_violation(
                f"DNS resolution failed for MCP endpoint host '{hostname}'.",
                url=url,
            ) from exc

        resolved: list[ipaddress.IPv4Address | ipaddress.IPv6Address] = []
        for addr_entry in addr_info_list:
            sockaddr = addr_entry[4]
            raw_ip = str(sockaddr[0]).split("%", 1)[0]
            try:
                parsed_ip = ipaddress.ip_address(raw_ip)
            except ValueError as exc:
                raise cls._build_security_violation(
                    f"Resolved invalid IP address '{raw_ip}' for host '{hostname}'.",
                    url=url,
                ) from exc
            if parsed_ip not in resolved:
                resolved.append(parsed_ip)

        if not resolved:
            raise cls._build_security_violation(
                f"DNS resolution returned zero IP records for MCP endpoint host '{hostname}'.",
                url=url,
            )

        return resolved

    @classmethod
    def _validate_ip_address(
        cls,
        *,
        ip_addr: ipaddress.IPv4Address | ipaddress.IPv6Address,
        url: str,
        allow_private_networks: bool,
    ) -> None:
        """Validate a single IPv4 or IPv6 address (and any IPv4-mapped address) against egress rules.

        Args:
            ip_addr: Resolved IPv4Address or IPv6Address to inspect.
            url: Original endpoint URL for structured error context.
            allow_private_networks: Whether loopback and private CIDR ranges are permitted.

        Raises:
            AppException: With ErrorCodes.SECURITY_VIOLATION if the IP address falls in a blocked range.
        """
        effective_ip: ipaddress.IPv4Address | ipaddress.IPv6Address = ip_addr
        if isinstance(ip_addr, ipaddress.IPv6Address) and ip_addr.ipv4_mapped is not None:
            effective_ip = ip_addr.ipv4_mapped

        if effective_ip in _CLOUD_METADATA_IPS or ip_addr in _CLOUD_METADATA_IPS:
            raise cls._build_security_violation(
                f"Resolved cloud metadata IP '{effective_ip}' is unconditionally blocked.",
                url=url,
            )

        if effective_ip.is_unspecified or effective_ip.is_multicast:
            raise cls._build_security_violation(
                f"Resolved unspecified or multicast IP '{effective_ip}' is blocked.",
                url=url,
            )

        if allow_private_networks:
            return

        if (
            effective_ip.is_loopback
            or effective_ip.is_private
            or effective_ip.is_link_local
            or effective_ip.is_reserved
        ):
            raise cls._build_security_violation(
                f"Resolved non-public IP '{effective_ip}' is blocked by SSRF egress policy.",
                url=url,
            )

    @classmethod
    def _build_security_violation(
        cls,
        reason: str,
        *,
        url: str,
    ) -> AppException:
        """Log structured security event and return AppException with ErrorCodes.SECURITY_VIOLATION.

        Args:
            reason: Human-readable mathematical/security failure reason.
            url: Target URL that triggered the violation.

        Returns:
            Configured AppException with status_code 403 and ErrorCodes.SECURITY_VIOLATION.
        """
        target_scheme = ""
        if url:
            target_scheme = urlparse(url).scheme
        logger.error(
            "MCP URL egress security violation",
            extra={
                "error_code": ErrorCodes.SECURITY_VIOLATION.value,
                "reason": reason,
                "target_scheme": target_scheme,
            },
        )
        return AppException(
            message=reason,
            status_code=403,
            details={"error_code": ErrorCodes.SECURITY_VIOLATION.value},
        )
