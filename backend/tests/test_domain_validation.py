import pytest
from app.utils.validators import sanitize_and_validate_domain

def test_valid_domains():
    assert sanitize_and_validate_domain("youtube.com") == "youtube.com"
    assert sanitize_and_validate_domain("HTTPS://YOUTUBE.COM/watch?v=123") == "youtube.com"
    assert sanitize_and_validate_domain("http://sub.domain.co.uk:8080/path") == "sub.domain.co.uk"
    assert sanitize_and_validate_domain("github.io") == "github.io"
    assert sanitize_and_validate_domain("localhost") == "localhost"

def test_invalid_domains():
    with pytest.raises(ValueError):
        sanitize_and_validate_domain("")
    with pytest.raises(ValueError):
        sanitize_and_validate_domain("not a domain")
    with pytest.raises(ValueError):
        sanitize_and_validate_domain("domain..com")
    with pytest.raises(ValueError):
        sanitize_and_validate_domain("youtube.com;DROP TABLE users")
    with pytest.raises(ValueError):
        sanitize_and_validate_domain("http://")
