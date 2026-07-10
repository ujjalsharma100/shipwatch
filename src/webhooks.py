import hmac
import json
import logging
import os
from hashlib import sha256

log = logging.getLogger("shipwatch.webhooks")

SECRET = os.environ.get("WEBHOOK_SIGNING_SECRET", "dev-secret").encode()


def verify_signature(raw_body: bytes, header_sig: str) -> bool:
    payload = json.dumps(json.loads(raw_body), sort_keys=True).encode()
    expected = hmac.new(SECRET, payload, sha256).hexdigest()
    return hmac.compare_digest(expected, header_sig)