"""Shared HTTP building blocks for talking to www.maccabipedia.co.il.

Two things every request to the wiki needs, and which this module centralises:

1. ``Accept: application/json`` — the host's Imunify360 WAF returns **HTTP 415
   "Unsupported Media Type"** to requests whose ``Accept`` header is the wildcard
   ``*/*`` (the default that ``requests`` and pywikibot send). The rule only fires
   for low-reputation / datacenter IPs, so it hit our scheduled CI jobs while the
   same URL succeeded from a residential connection. MediaWiki ignores ``Accept``
   (it picks the format from ``format=`` / CargoExport's ``&format=json``), so
   pinning a concrete value is purely to satisfy the WAF and never changes a body.
2. A retry ``Session`` across the wiki's transient edge blips (the openresty 415 /
   5xx window), so a single bad response doesn't fail a whole daily job.

pywikibot traffic is covered separately via ``extra_headers`` in
``pywikibot_configs/user-config.py``; this module is for the direct ``requests``
calls that bypass pywikibot.
"""
import logging
from urllib.parse import urlsplit

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

# Send a concrete Accept so the maccabipedia Imunify360 WAF doesn't 415 the wildcard */*.
MACCABIPEDIA_JSON_HEADERS = {"Accept": "application/json"}

# maccabipedia's edge occasionally serves a transient 415 (openresty proxy) or 5xx;
# retry across those blips instead of failing the daily job.
_RETRYABLE_STATUSES = (408, 415, 429, 500, 502, 503, 504)


def build_maccabipedia_session() -> requests.Session:
    """A ``requests.Session`` pre-configured for maccabipedia.co.il: WAF-safe
    ``Accept`` header + retry across the wiki's transient edge failures."""
    session = requests.Session()
    session.headers.update(MACCABIPEDIA_JSON_HEADERS)
    retry = Retry(
        total=5,
        backoff_factor=2,
        status_forcelist=_RETRYABLE_STATUSES,
        allowed_methods=frozenset(["GET"]),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    install_response_diagnostics(session)
    return session


# --- Diagnostics for the WAF block that outlived the Accept fix -----------------------
#
# Pinning `Accept: application/json` did stop the HTTP 415s (0 in 400 CI runs after the
# fix), but ~15% of scheduled runs still die on the FIRST call to the wiki with
# "API userinfo response lacks 'query' key" / "'str' object has no attribute 'items'" /
# "string indices must be integers". All three mean the same thing: the body parsed as
# JSON but came back as a *string* rather than the object MediaWiki owes us — i.e. an
# edge/WAF block page, not a wiki reply. We can't reproduce it locally (the Imunify360
# rule only fires for datacenter IPs), so instead of guessing we log the raw response the
# moment its shape is wrong. The next CI failure then carries the evidence to hand the host.

_BODY_SNIPPET_LIMIT = 800

# Response headers only, and only ones that identify the responder. Never log Set-Cookie
# (session token) and never touch the *request* body — the login POST carries the password.
_DIAGNOSTIC_HEADERS = (
    "Server",
    "Content-Type",
    "Content-Length",
    "Retry-After",
    "X-Powered-By",
    "CF-Ray",
    "X-Sucuri-ID",
    "X-Imunify360-Request-ID",
)


def _targets_maccabipedia(url: str) -> bool:
    host = urlsplit(url).hostname or ""
    return host == "maccabipedia.co.il" or host.endswith(".maccabipedia.co.il")


def _expects_json_body(url: str) -> bool:
    """True for the endpoints that must answer with a JSON object/array: the MediaWiki
    API and CargoExport. Plain article/Special: HTML fetches are not diagnosed."""
    split = urlsplit(url)
    return split.path.endswith("/api.php") or "format=json" in split.query


def describe_unexpected_response(response: requests.Response) -> str | None:
    """Why this maccabipedia response is not the JSON MediaWiki should have sent, or
    ``None`` when it looks fine. Split out from the hook so it is directly testable.

    Decided from the first non-whitespace byte rather than by parsing: this runs on every
    single response, and a Cargo chunk is 5000 rows that pywikibot/`.json()` is about to
    parse anyway. `{`/`[` open the object or array we expect, `"` is the bare JSON string
    the WAF block comes back as, anything else is not JSON at all.
    """
    if not _targets_maccabipedia(response.url):
        return None

    if response.status_code >= 400:
        return f"HTTP {response.status_code}"

    if not _expects_json_body(response.url):
        return None

    body_start = response.content[:_BODY_SNIPPET_LIMIT].lstrip()
    if not body_start:
        return "body is empty"

    first_character = body_start[:1]
    if first_character in (b"{", b"["):
        return None
    if first_character == b'"':
        # The exact shape behind all three CI crash signatures.
        return "JSON body is a bare string, expected an object or array"
    return "body is not JSON"


def _log_unexpected_response(response: requests.Response, *args, **kwargs) -> None:
    """``requests`` response hook. Returns ``None`` so the response passes through
    untouched — this only ever observes and logs, it never alters a run."""
    reason = describe_unexpected_response(response)
    if reason is None:
        return None

    headers = {
        name: response.headers[name]
        for name in _DIAGNOSTIC_HEADERS
        if name in response.headers
    }
    snippet = response.text[:_BODY_SNIPPET_LIMIT]
    truncated = " ...[truncated]" if len(response.text) > _BODY_SNIPPET_LIMIT else ""

    logger.error(
        "Unexpected response from maccabipedia (%s): %s %s | headers=%s | body=%r%s",
        reason,
        response.request.method,
        response.url,
        headers,
        snippet,
        truncated,
    )
    return None


def install_response_diagnostics(session: requests.Session) -> requests.Session:
    """Attach the unexpected-response logger to ``session``, once. Also usable on
    sessions we do not own — notably ``pywikibot.comms.http.session``."""
    hooks = session.hooks.setdefault("response", [])
    if _log_unexpected_response not in hooks:
        hooks.append(_log_unexpected_response)
    return session
