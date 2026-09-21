"""Convert MAC-address octet pairs into 192.168.x.x IP ranges."""

import re

MAC_PAIR_RE = re.compile(r"^([0-9A-Fa-f]{2})[:\-]?([0-9A-Fa-f]{2})$")

MAX_RANGE_SIZE = 512


class MacRangeError(ValueError):
    """Raised when user-supplied MAC octet input can't be parsed."""


def parse_mac_octet_pair(value: str) -> int:
    if not isinstance(value, str):
        raise MacRangeError("Neplatný formát MAC oktetů.")
    match = MAC_PAIR_RE.match(value.strip())
    if not match:
        raise MacRangeError(
            f"Neplatný formát '{value}'. Zadej dva hex bajty, např. AA:BB."
        )
    high, low = match.groups()
    return (int(high, 16) << 8) | int(low, 16)


def value_to_ip(value: int) -> str:
    octet3 = (value >> 8) & 0xFF
    octet4 = value & 0xFF
    return f"192.168.{octet3}.{octet4}"


def generate_ip_range(start_mac: str, end_mac: str) -> list[str]:
    start = parse_mac_octet_pair(start_mac)
    end = parse_mac_octet_pair(end_mac)
    if start > end:
        start, end = end, start
    if end - start + 1 > MAX_RANGE_SIZE:
        raise MacRangeError(
            f"Rozsah obsahuje {end - start + 1} adres, maximum je {MAX_RANGE_SIZE}."
        )
    return [value_to_ip(v) for v in range(start, end + 1)]
