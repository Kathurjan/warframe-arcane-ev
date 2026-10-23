import json, re, statistics

market = json.load(open("market.json"))
M = market["items"]

# ---- wiki: Module:Arcane/data -> Dissolution (Vosfor per rank-0 copy), MaxRank, Rarity
lua = open("arcane_data.lua", encoding="utf-8").read()
WIKI = {}
for m in re.finditer(r'\["([^"]+)"\]\s*=\s*\{(.*?)\n\t\t\}', lua, re.S):
    name, body = m.group(1), m.group(2)
    d = re.search(r"Dissolution\s*=\s*(\d+)", body)
    mr = re.search(r"MaxRank\s*=\s*(\d+)", body)
    ra = re.search(r'Rarity\s*=\s*"(\w+)"', body)
    WIKI[name.lower()] = {
        "name": name,
        "vosfor": int(d.group(1)) if d else None,
        "maxRank": int(mr.group(1)) if mr else None,
        "rarity": ra.group(1) if ra else None,
    }

def copies(rank):
    """Rank-0 copies consumed to reach `rank`: 1,3,6,10,15,21."""
    return (rank + 1) * (rank + 2) // 2

def by_name(name):
    for slug, it in M.items():
        if it["name"].lower() == name.lower():
            return slug
    return None

def ingame(it, typ, rank):
    return [o for o in it["orders"] if o["type"] == typ and o["rank"] == rank
            and o["visible"] and o["status"] == "ingame"]

def ask(it, rank):
    s = ingame(it, "sell", rank)
    return min(o["platinum"] for o in s) if s else None

def bid(it, rank):
    b = ingame(it, "buy", rank)
    return max(o["platinum"] for o in b) if b else None

def stat(it, rank, window):
    """Volume and volume-weighted median price of closed trades at `rank` over window."""
    rows = [r for r in it["stats"].get(window, []) if r.get("mod_rank", 0) == rank]
    if window == "90days":
        rows = rows[-7:]  # last 7 daily buckets
    vol = sum(r["volume"] for r in rows)
    if not vol:
        return 0, None
    pts = []
    for r in rows:
        pts += [r["median"]] * r["volume"]
    return vol, statistics.median(pts)

def price_info(slug, rank=0):
    it = M[slug]
    a, b = ask(it, rank), bid(it, rank)
    v48, m48 = stat(it, rank, "48hours")
    v7, m7 = stat(it, rank, "90days")
    med = m48 if v48 >= 3 else m7
    # Realistic sell: recent trade median, but never above the cheapest in-game
    # seller (you have to undercut them), and never below the best in-game buy order.
    cands = [x for x in (med, a) if x is not None]
    real = min(cands) if cands else None
    # Buy orders above the ask or >1.5x the trade median are bait/stale; ignore them.
    if b is not None and (a is None or b <= a) and (med is None or b <= 1.5 * med):
        real = max(real or 0, b)
    return {"ask": a, "bid": b, "vol48": v48, "med48": m48, "vol7d": v7, "med7d": m7,
            "real": real or 0, "list": a if a is not None else (med or 0)}
