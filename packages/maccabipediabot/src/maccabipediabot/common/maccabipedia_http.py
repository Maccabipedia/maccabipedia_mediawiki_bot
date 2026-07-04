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
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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
    return session
