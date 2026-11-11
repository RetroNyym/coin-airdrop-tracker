"""SQLite veritabani katmani - coin/airdrop kayitlari burada tutulur."""
import sqlite3
import time
import config

_SCHEMA = """
CREATE TABLE IF NOT EXISTS coins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,               -- hangi siteden bulundu (airdrops.io ...)
    url TEXT UNIQUE NOT NULL,           -- detay sayfasi adresi
    name TEXT,                          -- coin / airdrop basligi
    reward TEXT,                        -- ne kadar verilir (orn: 500 TOKEN)
    how_to TEXT,                        -- sartlar / nasil katilir
    exchange TEXT,                      -- hangi borsa platformu gecerli
    contract TEXT,                      -- kontrat adresi
    socials TEXT,                       -- twitter/telegram ... JSON
    flags TEXT,                         -- risk/kalite bayraklari JSON
    score REAL,                         -- 0..100 guven puani
    category TEXT,                      -- Guvenilir / Kismen / Riskli ...
    status TEXT DEFAULT '',             -- Aktif / Bitti (katilim durumu)
    first_seen INTEGER,                 -- unix ts, bot ilk ne zaman gordu
    last_seen INTEGER,                  -- unix ts
    last_updated INTEGER,
    html_title TEXT
);
"""

# Eski surumden gecen DB'lerde eksik kolonlari ekler
_ALTER_MIGRATIONS = [
    ("status", "ALTER TABLE coins ADD COLUMN status TEXT DEFAULT ''"),
]


def connect():
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with connect() as c:
        c.executescript(_SCHEMA)
        mevcut = {r[1] for r in c.execute("PRAGMA table_info(coins)")}
        for kolon, sql in _ALTER_MIGRATIONS:
            if kolon not in mevcut:
                try:
                    c.execute(sql)
                except sqlite3.OperationalError:
                    pass  # baska bir surec az once ekledi


def upsert_coin(c, rec):
    """Ayni URL mevcutsa guncelle, degilse yeni ekle."""
    now = int(time.time())
    c.execute(
        """INSERT INTO coins (source,url,name,reward,how_to,exchange,contract,
                              socials,flags,score,category,status,
                              first_seen,last_seen,last_updated,html_title)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
           ON CONFLICT(url) DO UPDATE SET
             name=excluded.name, reward=excluded.reward, how_to=excluded.how_to,
             exchange=excluded.exchange, contract=excluded.contract,
             socials=excluded.socials, flags=excluded.flags,
             score=excluded.score, category=excluded.category,
             status=excluded.status,
             last_seen=excluded.last_seen, last_updated=excluded.last_updated,
             html_title=excluded.html_title""",
        (rec["source"], rec["url"], rec.get("name"), rec.get("reward"),
         rec.get("how_to"), rec.get("exchange"), rec.get("contract"),
         rec.get("socials"), rec.get("flags"), rec.get("score"),
         rec.get("category"), rec.get("status", "Aktif"), now, now, now,
         rec.get("html_title")),
    )


def all_coins(c, order="score", status=None, source=None, q=None):
    """Filtreler: durum (Aktif/Bitti), kaynak site, ad/url/borsa aramasi."""
    # beraberlikleri kiracak ikincil siralama: ayni puandaki kayitlar her
    # yenilemede yer degistirmesin (kullanici 'siralama uygulanmiyor' sanir)
    order_sql = {
        "score": "score DESC, name ASC, id ASC",
        "fresh": "first_seen DESC, id DESC",
        "name": "name ASC, id ASC",
    }
    sql = "SELECT * FROM coins WHERE 1=1"
    args = []
    if status:
        sql += " AND status=?"
        args.append(status)
    if source:
        sql += " AND source=?"
        args.append(source)
    if q:
        sql += " AND (LOWER(name) LIKE ? OR LOWER(url) LIKE ? OR LOWER(exchange) LIKE ?)"
        args += [f"%{q.lower()}"] * 3
    sql += f" ORDER BY {order_sql.get(order, order_sql['score'])}"
    return [dict(r) for r in c.execute(sql, args)]


def sources(c):
    """Veritabaninda gecen kaynak sitelerin listesi."""
    return [r[0] for r in c.execute("SELECT DISTINCT source FROM coins ORDER BY source")]
