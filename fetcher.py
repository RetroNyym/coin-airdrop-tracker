"""Orak HTTP yardimcisi: gecikme + yeniden deneme + temiz session."""
import time
import requests
import config

_session = requests.Session()
_session.headers.update({"User-Agent": config.USER_AGENT,
                         "Accept-Language": "en-US,en;q=0.9,tr;q=0.8"})


def get(url, **kw):
    """Basit GET, hata olursa None doner (bot calismaya devam eder)."""
    time.sleep(config.REQUEST_DELAY)
    try:
        r = _session.get(url, timeout=config.REQUEST_TIMEOUT, **kw)
        if r.status_code == 200 and r.text:
            return r.text
        print(f"[http] {url} -> durumu {r.status_code}")
    except Exception as e:
        print(f"[http] HATA {url}: {e}")
    return None
