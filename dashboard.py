"""
CoinBot Dashboard - localhost paneli.
Arka planda surekli tarama dongusu + basit web arayuzu.
"""
import threading
import webbrowser
import time
import sys
import config
import database
import scrapers


def _fmt_ts(ts):
    """Unix zaman damgasini okunur metne cevirir."""
    if not ts:
        return "—"
    import datetime
    d = datetime.datetime.fromtimestamp(int(ts))
    return d.strftime("%d.%m.%Y %H:%M")


def _from_json(s):
    import json
    try:
        return json.loads(s or "[]")
    except Exception:
        return []


def scan_loop():
    """Girildigi surece periyodik tarama yapar."""
    while True:
        try:
            t0 = time.time()
            new = scrapers.run_scan()
            print(f"[bot] tarama bitti: {len(new)} kayit islendi, "
                  f"{time.time()-t0:.1f} sn surdu")
        except Exception as e:
            print(f"[bot] dongu hatasi: {e}")
        time.sleep(config.SCAN_INTERVAL_SECONDS)


def build_app():
    from flask import Flask, render_template, request
    app = Flask(__name__)

    app.jinja_env.filters["topic_ts"] = _fmt_ts
    app.jinja_env.filters["from_json"] = _from_json

    def _filter_args():
        """Ortak filtre argumanlarini toplayan yardimci."""
        return {
            "order": request.args.get("order", "score"),
            "q": (request.args.get("q") or "").strip(),
            "cat": request.args.get("cat", ""),
            "status": request.args.get("status", ""),
            "source": request.args.get("source", ""),
        }

    @app.route("/")
    def index():
        f = _filter_args()
        with database.connect() as c:
            coins = database.all_coins(c, order=f["order"], q=f["q"],
                                       status=f["status"] or None,
                                       source=f["source"] or None)
        filt = [k for k in coins if not f["cat"] or k["category"] == f["cat"]]
        return render_template("index.html", coins=filt, **ortak(f, coins))

    @app.route("/drops")
    def drops():
        """Ayrilmis tam drop/airdrop listesi: tum kaynaklar, durum ve tarih ile."""
        f = _filter_args()
        with database.connect() as c:
            coins = database.all_coins(c, order=f["order"], q=f["q"],
                                       status=f["status"] or None,
                                       source=f["source"] or None)
            src_list = database.sources(c)
        ctx = ortak(f, coins)
        ctx["sources"] = src_list
        return render_template("drops.html", coins=coins, **ctx)

    def ortak(f, coins):
        """Sablonlara gecilecek ortak degisken paketi."""
        return {
            "order": f["order"], "q": f["q"], "cat": f["cat"],
            "status": f["status"], "source": f["source"],
            "cats": ["Guvenilir", "Kismen Guvenilir", "Az Guvenilir", "Riskli"],
            "stats": {
                "aktif": sum(1 for k in coins if k.get("status") == "Aktif"),
                "bitti": sum(1 for k in coins if k.get("status") == "Bitti"),
                "toplam": len(coins),
            },
        }

    @app.route("/coin/<int:cid>")
    def detail(cid):
        with database.connect() as c:
            r = c.execute("SELECT * FROM coins WHERE id=?", (cid,)).fetchone()
            coin = dict(r) if r else None
        if not coin:
            return "Kayit bulunamadi", 404
        return render_template("detail.html", coin=coin)

    @app.route("/api/coins")
    def api():
        with database.connect() as c:
            return {"coins": database.all_coins(c, request.args.get("order", "score"))}

    return app


def main():
    database.init_db()

    # Tarama dongusunu arka planda baslat
    threading.Thread(target=scan_loop, daemon=True).start()
    # Ilk taramayi beklemeden balansli gosterme icin hemen bir kez tetikle
    threading.Thread(target=scrapers.run_scan, daemon=True).start()

    app = build_app()
    url = f"http://{config.DASHBOARD_HOST}:{config.DASHBOARD_PORT}"
    print("=" * 56)
    print("  CoinBot dashboard calisiyor ->", url)
    print("  Tarayici otomatik acilacak; pencereyi kapatabilirsin.")
    print("=" * 56)
    threading.Timer(1.5, lambda: webbrowser.open(url)).start()

    try:
        app.run(host=config.DASHBOARD_HOST, port=config.DASHBOARD_PORT,
                debug=False)
    except KeyboardInterrupt:
        pass
    sys.exit(0)


if __name__ == "__main__":
    main()
