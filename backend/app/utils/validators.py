import re
from urllib.parse import urlparse

DOMAIN_REGEX = re.compile(
    r"^(?:[a-zA-Z0-9]"
    r"(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+"
    r"[a-zA-Z]{2,63}$"
)

def sanitize_and_validate_domain(raw_domain: str) -> str:
    """
    Cleans and strictly validates a domain string.
    Strips protocol, paths, query params, ports, and converts to lowercase.
    Raises ValueError if domain is invalid.
    """
    if not raw_domain or not isinstance(raw_domain, str):
        raise ValueError("Domain must be a non-empty string.")

    cleaned = raw_domain.strip().lower()

    # If scheme is present, parse it with urlparse
    if "://" in cleaned:
        parsed = urlparse(cleaned)
        cleaned = parsed.netloc or parsed.path
    elif "/" in cleaned:
        cleaned = cleaned.split("/")[0]

    # Remove port if present
    if ":" in cleaned:
        cleaned = cleaned.split(":")[0]

    # Support localhost for local dev/testing
    if cleaned in ("localhost", "127.0.0.1"):
        return cleaned

    # Check overall length
    if len(cleaned) > 253 or len(cleaned) < 3:
        raise ValueError(f"Domain length invalid: {cleaned}")

    if not DOMAIN_REGEX.match(cleaned):
        raise ValueError(f"Invalid domain format: '{cleaned}'. Must be a valid domain such as 'youtube.com'.")

    return cleaned
