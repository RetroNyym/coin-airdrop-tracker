"""
Genel amaçlı airdrop sayfasi kaziyici.

Sitelere ayri ayri ozel kod yazmak yerine, config'deki link desenine uyan
detay sayfalarini bulup her birini ortak bir parser ile isler. Boylece
yeni bir 'coin veren' siteyi config.py'a satir ekleyerek tanitabilirsin.
"""
import re
import json
import config
import fetcher
from bs4 import BeautifulSoup

# Bilinen borsalar (exchange tespiti icin)
EXCHANGES = ["binance", "bybit", "okx", "kucoin", "gate.io", "mexc", "bitget",
             "kraken", "coinbase", "huobi", "htx", "bitfinex",
             "poloniex", "lbank", "bithumb", "upbit", "ascendex", "coingecko",
             "coinmarketcap"]

# Sosyal medya alan adlari
SOCIAL_DOMAINS = {"twitter.com", "x.com", "t.me", "telegram.me", "discord.gg",
                  "discord.com", "medium.com", "reddit.com", "youtube.com"}

ETH_ADDR = re.compile(r"0x[a-fA-F0-9]{40}")
REWARD = re.compile(
    r"(\d[\d,.]*\s*(?:tokens?|usdt|usdc|usd+|bnb|eth|sol|matic)\b.{0,40})", re.I)

# Her sitede arama yaparlar: nav,车库, contact gibi detaysayfa olmayan linkler
NON_DETAIL = {"about", "contact", "privacy", "terms", "faq", "home", "blog",
              "advertise", "disclaimer", "submit-airdrop", "submit"}


def _detail_url(domain, href):
    """Bagil linki mutlak adrese cevirir."""
    if href.startswith("http"):
        return href
    return domain + ("" if href.startswith("/") else "/") + href


def is_detail(url, domain, cfg):
    """Bu bir detay sayfasi mi? (path deseni + nav linkleri ayiklama)"""
    if not url.startswith(domain):
        return False
    path = url[len(domain):].strip("/")
    parts = [p for p in path.split("/") if p]
    if not parts or parts[0] in NON_DETAIL or "/".join(parts) in cfg.get("exclude", []):
        return False
    # kaynak ozel path deseni (en guvenilir yontem)
    pat = cfg.get("path_pattern")
    if pat:
        return re.match(pat, "/" + "/".join(parts) + "/") is not None
    pat = cfg.get("link_pattern")
    if pat:
        return len(parts) == 1 and re.search(pat, parts[0]) is not None
    return False


def parse_detail(html, url):
    """Airdrop detay sayfasindan yapilandirilmis veri cikartir."""
    soup = BeautifulSoup(html, "lxml")
    # menu/header/footer'i cikart: nav linkleri (orn 'Ended Airdrops') durum
    # tespitini bozmasin ve footer'daki '2026 Siteadi' reward'a yakalanmasin
    for tag in soup.find_all(["nav", "header", "footer"]):
        tag.decompose()
    text = " ".join(stripped(x.get_text(" ")) for x in soup.find_all(string=True))
    title = ""
    t = soup.find("h1")
    if t:
        title = stripped(t.get_text(" "))[:120]
    else:
        og = soup.find("meta", {"property": "og:title"})
        if og and og.get("content"):
            title = og["content"][:120]

    # Sosyal linkler
    socials = set()
    for a in soup.find_all("a", href=True):
        h = a["href"].lower()
        for d in SOCIAL_DOMAINS:
            if d in h:
                socials.add(_socials_clean(h))
                break

    # Kontrat adresi
    addr_m = ETH_ADDR.search(text)
    contract = addr_m.group(0) if addr_m else ""

    # Borsa adlari
    low = re.sub(r"gate\.?io|gate\.? rnd", "gate.io", text.lower())
    found_ex = sorted({e.title() for e in EXCHANGES if e in low})

    # Odul miktarı (reward)
    rc = REWARD.search(text)
    reward = rc.group(0)[:60] if rc else ""

    # Nasil katilir: sirali liste ogelerini toplayarak
    steps = []
    for ul in soup.find_all("ul", limit=14):
        items = [stripped(li.get_text(" ")) for li in ul.find_all("li")][:6]
        if 3 <= len(" ".join(items)) <= 800 and items:
            steps.append(items)
    how_to = " | ".join("• " + s for grp in steps[:2] for s in grp[:4])

    # Kalite/risk bayraklari
    lowtext = text.lower()
    flags = {}
    keywords = {
        "kyc": ["kyc required", "kyc necessary", "identity verification"],
        "paid": ["deposit required", "you must invest", "paid listing",
                 "buy to claim", "investment required"],
        "audit": ["audit", "audited by", "certik", "hacken", "peckshield"],
        "deadline": ["deadline", "ends on", "closes on", "ends in"],
    }
    for k, needles in keywords.items():
        flags[k] = any(n in lowtext for n in needles)

    # durum: airdrop bitmis mi hala katilabilir mi
    # (genel 'ended' kelimesi nav'da gecer, net ifadeler ariyoruz)
    if any(n in lowtext for n in ["airdrop has ended", "has ended", "has closed",
                                  "campaign ended", "registration closed",
                                  "airdrop is closed", "airdrop is expired"]):
        status = "Bitti"
    else:
        status = "Aktif"

    return {
        "url": url,
        "name": title,
        "html_title": (soup.title.string or "").strip()[:120] if soup.title else title,
        "status": status,
        "reward": reward, "how_to": how_to[:900], "exchange": ", ".join(found_ex[:6]),
        "contract": contract, "socials": json.dumps(sorted(socials), ensure_ascii=False),
        "flags": json.dumps(flags, ensure_ascii=False),
    }


def _socials_clean(h):
    # gereksiz query parametrelerinden arindir
    h = h.split("?", 1)[0].lower()
    return h[:120]


def stripped(s):
    return re.sub(r"\s+", " ", (s or "").strip())


def _list_entries(cfg):
    """list_urls'te hem sade URL hem {'url':..,'status':..} kabul eder."""
    out = []
    for it in cfg["list_urls"]:
        if isinstance(it, dict):
            out.append(it)
        else:
            out.append({"url": it, "status": None})
    return out


def scan_source(name, cfg, limit):
    """Bir kaynagin tum liste sayfalarindaki detay linkleri + detay cekim."""
    links = []
    seen = set()
    status_by_url = {}
    for ent in _list_entries(cfg):
        html = fetcher.get(ent["url"])
        if not html:
            continue
        soup = BeautifulSoup(html, "lxml")
        for a in soup.select(cfg["link_selector"]):
            href = a.get("href", "")
            if not href:
                continue
            u = _detail_url(cfg["domain"], href)
            if u not in seen and is_detail(u, cfg["domain"], cfg):
                seen.add(u)
                links.append(u)
                status_by_url[u] = ent["status"]
    links = links[:limit]

    out = []
    for u in links[:limit]:
        h = fetcher.get(u)
        if not h:
            continue
        rec = parse_detail(h, u)
        # kaynak listesinden gelen durum bilgisi (orn: expired sayfasi -> Bitti)
        rec["status"] = status_by_url.get(u) or rec.get("status") or "Aktif"
        rec["source"] = name
        out.append(rec)
    return out


def run_scan():
    """Tum kaynaklari tarar, skorlar ve veritabanina kaydeder."""
    from scoring import score_coin
    import database
    results = []
    for name, cfg in config.SOURCES.items():
        try:
            results.extend(scan_source(name, cfg, config.DETAIL_LIMIT_PER_SOURCE))
        except Exception as e:
            print(f"[scan] {name} hata: {e}")
    if not results:
        return []
    with database.connect() as c:
        for rec in results:
            s, cat = score_coin(rec)
            rec["score"], rec["category"] = s, cat
            database.upsert_coin(c, rec)
    return results
