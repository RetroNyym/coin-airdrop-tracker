"""
Cagirici/scan ayarlari. Buradaki degerleri degistirerek botun
davranisini kod yazmadan kontrol edebilirsin.
"""
import pathlib
import os

# Proje klasoru
BASE_DIR = pathlib.Path(__file__).parent
DB_PATH = BASE_DIR / "coinbot.db"

# --- Tarama ---
# Airdrop listesi kaynaklari (ana sayfa URL'si -> detay linkini taniyan CSS secici)
SOURCES = {
    "airdrops.io": {
        "list_urls": [
            "https://airdrops.io/latest/",
            "https://airdrops.io/hot/",
            {"url": "https://airdrops.io/expired/", "status": "Bitti"},
        ],
        "link_selector": "a[href]",
        "path_pattern": r"^/[a-z0-9-]+/$",
        "exclude": ["latest", "hot", "expired", "airdrop-alert"],
        "domain": "https://airdrops.io",
    },
    "gemdrops.io": {
        "list_urls": ["https://gemdrops.io/airdrops"],
        "link_selector": "a[href]",
        "path_pattern": r"^/projects/[a-z0-9-]+/$",
        "exclude": [],
        "domain": "https://gemdrops.io",
    },
    "alphadrops.net": {
        "list_urls": ["https://alphadrops.net/airdrops"],
        "link_selector": "a[href]",
        "path_pattern": r"^/airdrops/[a-z0-9-]+/?$",
        "exclude": [],
        "domain": "https://alphadrops.net",
    },
    "defillama.com": {
        "list_urls": ["https://defillama.com/airdrops"],
        "link_selector": "a[href]",
        "path_pattern": r"^/protocol/[a-z0-9-]+/?$",
        "exclude": [],
        "domain": "https://defillama.com",
    },
    "coingabbar.com": {
        "list_urls": ["https://www.coingabbar.com/en/crypto-airdrops"],
        "link_selector": "a[href]",
        "path_pattern": r"^/en/crypto-airdrops/[a-z0-9-]+/?$",
        "exclude": [],
        "domain": "https://www.coingabbar.com",
    },
}

# Her kaynak icin kaclar detay sayfasina gidilecegi (sayfa detaylarina ulasmak icin)
DETAIL_LIMIT_PER_SOURCE = 15

# Tarama dongusu araligi (saniye) - dashboard arka planda bu aralikla tarar
SCAN_INTERVAL_SECONDS = 30 * 60  # 30 dk

# Istekler arasi nazik bekleme (saniye) - siteyi bozmamak icin
REQUEST_DELAY = 1.5
REQUEST_TIMEOUT = 20

USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

# --- Dashboard ---
DASHBOARD_HOST = "127.0.0.1"
DASHBOARD_PORT = 8787

# --- Guven puani agirliklari (toplam 100) ---
WEIGHTS = {
    "contract": 18,        # adres/Kontrat bilgisi paylasmis
    "social": 14,          # sosyal medya linkleri aktifgorunuyor
    "exchange": 16,        # bilinen borsaya listed / mention
    "audit": 12,           # audit/KYC yazi-kotentordablin
    "detail": 15,          # net detay: miktar, sartlar, tarih
    "transparency": 10,    # ekiple yasa/ son tarih/rule netligi
    "freshness": 10,       # yenilik (listeye yeni girme)
    "paid_penalty": -25,   # ucret istiyorsa ceza
}

