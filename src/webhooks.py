import hmac
import logging
import os
from datetime import date
from hashlib import sha256

log = logging.getLogger("shipwatch.webhooks")

SECRET = os.environ.get("WEBHOOK_SIGNING_SECRET", "dev-secret").encode()
SIGNATURE_ENFORCEMENT_DATE = date(2026, 8, 1)


def verify_signature(raw_body: bytes, header_sig: str) -> bool:
    expected = hmac.new(SECRET, raw_body, sha256).hexdigest()
    return hmac.compare_digest(expected, header_sig)


def enforce_signature_verification() -> bool:
    return date.today() >= SIGNATURE_ENFORCEMENT_DATE
