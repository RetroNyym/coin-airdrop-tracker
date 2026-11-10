# CoinBot — Coin Veren Siteler Tarayıcı + Güven Puanı Paneli

İnternetteki airdrop / "coin veren" siteleri düzenli olarak tarar,
her coin için **faktör bazlı güven puanı (%0-100)** hesaplar ve
localhost'ta çalışan bir **web dashboard** üzerinde gösterir.

## Ne yapar?

- **Tarama:** airdrops.io gibi kaynakların liste sayfalarını ("latest", "hot")
  tarar, bulduğu **her coinin detay sayfasına girer** ve çıkarır:
  - coin başlığı, hangi sitede listelendiği
  - reward / ne kadar verilecek (örn. "350 USDT")
  - programa hangi borsa üzerinden katılabileceğin (binance, bybit, kucoin...)
  - katılım adımları (nasil alinir)
  - kontrat adresi (0x...), sosyal medya linkleri
  - risk/kalite bayrakları (KYC zorunlu mu, ücret istiyor mu, audit var mı, son tarih)
- **Güven puanı (0-100):**

  | Faktör | Ağırlık | Ne bakılıyor |
  |---|---|---|
  | Kontrat paylaşımı | 18 | 0x... kontrat adresi paylaşılmış mı |
  | Borsa bağlantısı | 16 | bilinen hangi borsa ile anılıyor |
  | Detay netliği | 15 | net reward miktarı + katılım adımları var mı |
  | Sosyal aktivite | 14 | twitter/telegram/discord linkleri |
  | Audit / KYC | 12 | denetim bahsi geçiyor mu |
  | Şeffaflık | 10 | adım adım talimat netliği |
  | Güncellik | 10 | temel puandır |
  | ÜCRET İSTİYORSA | **−25** | "deposit required / buy to claim" uyarısı ciddi cezaya düşürür |

  Puan aralığına göre kategori: **Güvenilir (75+)**, **Kısmen Güvenilir (55-74)**,
  **Az Güvenilir (35-54)**, **Riskli (<35)**

- **Dashboard (http://127.0.0.1:8787):**
  - **Güven Panosu (`/`)**: puan sıralaması, kategori filtreleri, arama, 60 sn'de bir otomatik yenileme
  - **Airdrop Listesi (`/drops`)**: tüm drop/airdrop kayıtları tek tabloda — Aktif/Bitmiş durumu,
    reward, kaynak site, bulunma zamanı, borsa, ücret/KYC/audit bayrakları; durum ve kaynak filtreleri
  - `/coin/<id>`: her coinin tam detay sayfası (nasıl alınır, borsa, kontrat, sosyal linkler)
  - `/api/coins`: JSON çıktısı (başka bir uygulamada kullanmak için)

## İzlenen kaynaklar

Bot varsayılan olarak şu siteleri tarar (`config.py → SOURCES`):

| Kaynak | Ne içerir |
|---|---|
| airdrops.io | latest + hot listeleri, expired arşiv |
| gemdrops.io | aktif airdrop/proje kartları |
| alphadrops.net | geniş airdrop kataloğu |
| defillama.com | protokol airdrop panosu |
| coingabbar.com | tablo bazlı airdrop listesi (reward + tarih) |

## Nasıl çalıştırılır?

```
baslat.bat  (çift tıkla)
# veya
python dashboard.py
```

Bot arka planda **30 dakikada bir** yeniden tarar (ayar: `config.py → SCAN_INTERVAL_SECONDS`).
Panel tarayıcıda otomatik açılır.

## Yeni site ekleme

`config.py` içindeki `SOURCES` sözlüğüne yeni girdi ekle:

```python
"yenisite.com": {
    "list_urls": ["https://yenisite.com/latest/"],
    "link_selector": "a[href]",
    "link_pattern": r"^[a-z0-9-]{3,60}$",   # detay linki deseni
    "exclude": ["about", "contact", ...],   # detay olmayan yollar
    "domain": "https://yenisite.com",
},
```

Bot, desenlere uyan detay sayfalarını otomatik tanır ve puanlar.

## Önemli notlar

- Puan **otomatik tahmindir**, sizi yatırım dolandırıcılığından tek başına korumaz —
  her coin'i cüzdanını bağlamadan önce kendin de kontrol et (DYOR).
- Kaynak site HTML düzeni değişirse sorun olabilir; `config.py` içindeki
  `link_pattern`/`exclude` düzenlemesi çoğunlukla yeterli.
- Veriler `CoinBot/coinbot.db` dosyasında tutulur; bu dosyayı silerek
  veri tabanını sıfırlayabilirsin.
