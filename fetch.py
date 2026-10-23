"""Download the data the analysis scripts need.

arcane_data.lua: Vosfor dissolution value, max rank and rarity per Arcane (Warframe wiki).
market.json: live warframe.market orders and trade statistics for every tradable Arcane.
Rate limited to about 3 requests per second (warframe.market's limit)."""
import json, time, urllib.request, datetime

UA = {"User-Agent": "arcane-ev/1.0", "Platform": "pc", "Language": "en"}

def get(url, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception as e:
            print("  retry", url, e)
            time.sleep(2 + 2 * i)
    return None

WIKI_DATA = "https://wiki.warframe.com/w/Module:Arcane/data?action=raw"
req = urllib.request.Request(WIKI_DATA, headers={"User-Agent": UA["User-Agent"]})
with urllib.request.urlopen(req, timeout=30) as r:
    open("arcane_data.lua", "w", encoding="utf-8").write(r.read().decode("utf-8"))
print("saved arcane_data.lua")

items = get("https://api.warframe.market/v2/items")["data"]
arcanes = [x for x in items if "arcane_enhancement" in x.get("tags", [])]
print(len(arcanes), "arcanes")

out = {"fetched_utc_start": datetime.datetime.now(datetime.timezone.utc).isoformat(), "items": {}}
for n, a in enumerate(arcanes):
    slug = a["slug"]
    orders = get(f"https://api.warframe.market/v2/orders/item/{slug}")
    time.sleep(0.35)
    stats = get(f"https://api.warframe.market/v1/items/{slug}/statistics")
    time.sleep(0.35)
    out["items"][slug] = {
        "name": a["i18n"]["en"]["name"],
        "maxRank": a.get("maxRank"),
        "tags": a.get("tags"),
        "orders": [
            {k: o[k] for k in ("type", "platinum", "quantity", "rank", "visible")}
            | {"status": o["user"]["status"]}
            for o in (orders or {}).get("data", [])
        ],
        "stats": (stats or {}).get("payload", {}).get("statistics_closed", {}),
    }
    if n % 20 == 0:
        print(n, slug)

out["fetched_utc_end"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
json.dump(out, open("market.json", "w"))
print("done", out["fetched_utc_start"], "->", out["fetched_utc_end"])
