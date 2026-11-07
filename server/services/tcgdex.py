import os
import urllib.request
import urllib.parse
import json
import re
import concurrent.futures

TCGDEX_BASE = os.environ.get("CC_TCGDEX_BASE", "https://api.tcgdex.net/v2")
TCG_LANG = os.environ.get("CC_TCG_LANG", "es")

class ApiError(Exception):
    def __init__(self, code, msg):
        super().__init__(msg)
        self.code = code
        self.msg = msg

def norm_number(n):
    if not n:
        return ""
    n = str(n).split("/")[0].strip()
    return str(int(n)) if n.isdigit() else n

def tcgdex_get(path, params=None, timeout=20):
    url = TCGDEX_BASE + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "CardCollector/1.0", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise ApiError(502, f"Error en TCGdex ({e.code})")
    except Exception as e:
        raise ApiError(502, f"Error de conexión con TCGdex: {e}")

def fetch_card(card_id):
    if not card_id:
        return None
    for lang in [TCG_LANG, "en"]:
        try:
            card = tcgdex_get(f"/{lang}/cards/{urllib.parse.quote(card_id)}")
            if card and isinstance(card, dict) and card.get("id"):
                return card
        except Exception:
            continue
    return None

def simplify(c):
    if not c or not isinstance(c, dict):
        return {}
    pricing = c.get("pricing") or {}
    cm = pricing.get("cardmarket") or c.get("cardmarket") or {}
    tp = pricing.get("tcgplayer") or c.get("tcgplayer") or {}
    
    eur = cm.get("trend") or cm.get("avg") or cm.get("low") or (cm.get("prices") or {}).get("averageSellPrice") or 0.0
    usd = 0.0
    for v in ["normal", "holofoil", "reverse-holofoil", "unlimited"]:
        p = tp.get(v) or (tp.get("prices") or {}).get(v)
        if isinstance(p, dict):
            m = p.get("marketPrice") or p.get("midPrice") or p.get("lowPrice")
            if m is not None:
                usd = float(m)
                break

    img_base = c.get("image") or ""
    if not img_base and c.get("images"):
        imgs = c.get("images")
        if isinstance(imgs, str):
            img_base = imgs
        elif isinstance(imgs, dict):
            img_base = imgs.get("image") or imgs.get("large") or imgs.get("small") or ""

    img_url = (img_base + "/low.webp") if img_base and not img_base.endswith(".webp") else img_base

    set_info = c.get("set") or {}
    cnt = set_info.get("cardCount") or {}
    printed_total = cnt.get("official") or cnt.get("total")

    return {
        "id": c.get("id"),
        "name": c.get("name", ""),
        "number": str(c.get("localId") or c.get("number") or ""),
        "total": printed_total,
        "rarity": c.get("rarity") or "Común",
        "set": set_info.get("name") if isinstance(set_info, dict) else (set_info or "Sin Expansión"),
        "image": img_url,
        "price_eur": float(eur or 0.0),
        "price_usd": float(usd or 0.0),
        "cardmarket_url": f"https://www.cardmarket.com/es/Pokemon/Products/Singles?searchString={urllib.parse.quote(c.get('name',''))}",
        "tcgplayer_url": f"https://www.tcgplayer.com/search/pokemon/product?q={urllib.parse.quote(c.get('name',''))}"
    }

def search_cards(name, number="", total="", set_name=""):
    name = (name or "").strip()
    if not name:
        return []

    # Se busca por nombre limpio en español e inglés como fallback
    briefs = []
    for lang in [TCG_LANG, "en"]:
        try:
            res = tcgdex_get(f"/{lang}/cards", params={"name": name})
            if res and isinstance(res, list):
                briefs = res
                break
        except Exception:
            pass

    # Si no hay resultados directos, intentar buscar solo la primera palabra (ej: 'Meowth')
    if not briefs and " " in name:
        first_word = name.split()[0]
        for lang in [TCG_LANG, "en"]:
            try:
                res = tcgdex_get(f"/{lang}/cards", params={"name": first_word})
                if res and isinstance(res, list):
                    briefs = res
                    break
            except Exception:
                pass

    if not briefs:
        return []

    n = norm_number(number)
    sn = (set_name or "").lower().strip()

    def pre_score(b):
        sc = 0
        b_num = norm_number(b.get("localId", ""))
        if n and b_num == n:
            sc += 50
        b_name = (b.get("name") or "").lower()
        if b_name == name.lower():
            sc += 50
        return -sc

    briefs.sort(key=pre_score)
    top_briefs = briefs[:15]

    with concurrent.futures.ThreadPoolExecutor(max_workers=min(10, len(top_briefs) or 1)) as ex:
        details = list(ex.map(lambda b: fetch_card(b.get("id")), top_briefs))

    cands = [simplify(d) for d in details if d]

    def final_score(c):
        sc = 0
        c_num = norm_number(c.get("number", ""))
        if n and c_num == n:
            sc += 60
        if c.get("name", "").lower() == name.lower():
            sc += 40
        if sn and sn in (c.get("set") or "").lower():
            sc += 30
        return -sc

    cands.sort(key=final_score)
    return cands[:12]

def refresh_cards(ids):
    out = {}
    valid_ids = [i for i in ids if isinstance(i, str) and len(i) < 50]
    if not valid_ids:
        return out
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(10, len(valid_ids))) as ex:
        cards = list(ex.map(fetch_card, valid_ids))
    for c in cards:
        if c:
            s = simplify(c)
            out[s["id"]] = s
    return out