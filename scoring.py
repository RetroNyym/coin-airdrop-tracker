"""
Faktor bazli guven puani (0-100).

Her coin; kontrat paylasimi, sosyal aktiflik, borsa baglantiyi, audit bildirilmesi,
detay netligi, lots of criteria uzerinden puan alir.
"""
import json
import time
import math
import config


def score_coin(rec):
    w = config.WEIGHTS
    total = sum(v for v in w.values())  # agirlik toplami
    score = 0

    def add(when, weight):
        nonlocal score
        if when:
            score += weight

    contract = rec.get("contract") or ""
    socials = _load_json(rec.get("socials"))
    exchange = (rec.get("exchange") or "")
    flags = _load_json(rec.get("flags"))
    reward = rec.get("reward") or ""
    how_to = rec.get("how_to") or ""

    def add(points, weight):
        """points: 0..1 arasi gerceklesme orani -> agirliklaniyor"""
        nonlocal score
        score += weight * max(0.0, min(1.0, points))

    ex_count = len([e for e in exchange.split(",") if e.strip()])
    add(1.0 if len(contract) == 42 else 0.0, w["contract"])
    add(min(len(socials), 3) / 3.0, w["social"])
    add(min(ex_count, 2) / 2.0, w["exchange"])
    add(1.0 if flags.get("audit") else 0.0, w["audit"])
    add((0.5 if reward else 0.0) + (0.5 if how_to else 0.0), w["detail"])
    add(1.0 if (len(how_to) > 150 and ("•" in how_to)) else 0.3, w["transparency"])
    add(0.6, w["freshness"])  # temel puan; ileride 'first_seen' eskidikce dusurulebilir

    if flags.get("paid") and not flags.get("audit"):
        add(1.0, w["paid_penalty"])  # negatif agirlik

    score = max(0.0, min(100.0, score / total * 100))
    return round(score, 1), category(score)


def category(score):
    if score >= 75:
        return "Guvenilir"
    if score >= 55:
        return "Kismen Guvenilir"
    if score >= 35:
        return "Az Guvenilir"
    return "Riskli"


def _load_json(s):
    try:
        v = json.loads(s or "[]")
        return v if isinstance(v, (list, dict)) else []
    except Exception:
        return []
