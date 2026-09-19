#!/usr/bin/env python3
import json, os, pathlib, urllib.parse, urllib.request
from datetime import datetime, timezone

BASE = "https://api.the-odds-api.com/v4"
SPORT = os.getenv("SPORT_KEY", "soccer_epl")
REGIONS = os.getenv("ODDS_REGIONS", "us")
BOOKS = os.getenv("ODDS_BOOKMAKERS", "fanduel,draftkings,fanatics")
API_KEY = os.environ["ODDS_API_KEY"]
OUT = pathlib.Path("data/odds")
OUT.mkdir(parents=True, exist_ok=True)

def get(path, **params):
    params["apiKey"] = API_KEY
    url = f"{BASE}{path}?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "EDGE-FC/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r), dict(r.headers)

def main():
    now = datetime.now(timezone.utc)
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    events, _ = get(f"/sports/{SPORT}/events")
    raw = {"fetched_at": now.isoformat(), "sport": SPORT, "events": events, "event_markets": []}

    markets = [
        "h2h", "totals", "btts", "correct_score", "correct_score_h1",
        "player_shots", "player_shots_on_target",
        "alternate_totals_corners", "alternate_team_totals_corners"
    ]
    for ev in events:
        eid = ev.get("id")
        for market in markets:
            try:
                payload, _ = get(
                    f"/sports/{SPORT}/events/{eid}/odds",
                    regions=REGIONS, bookmakers=BOOKS, markets=market,
                    oddsFormat="american", dateFormat="iso"
                )
                raw["event_markets"].append({"event_id": eid, "market": market, "data": payload})
            except Exception as exc:
                raw["event_markets"].append({"event_id": eid, "market": market, "error": str(exc)[:300]})

    raw_path = OUT / f"epl_raw_{stamp}.json"
    raw_path.write_text(json.dumps(raw, indent=2), encoding="utf-8")

    rows = []
    for item in raw["event_markets"]:
        data = item.get("data")
        if not isinstance(data, dict):
            continue
        base = {
            "event_id": data.get("id"), "commence_time": data.get("commence_time"),
            "home_team": data.get("home_team"), "away_team": data.get("away_team")
        }
        for book in data.get("bookmakers", []):
            for market in book.get("markets", []):
                for outcome in market.get("outcomes", []):
                    rows.append({
                        **base, "bookmaker": book.get("key"), "bookmaker_title": book.get("title"),
                        "market": market.get("key"), "last_update": market.get("last_update"),
                        "name": outcome.get("name"), "description": outcome.get("description"),
                        "price": outcome.get("price"), "point": outcome.get("point")
                    })

    latest = {"fetched_at": now.isoformat(), "sport": SPORT, "bookmakers": BOOKS.split(","), "rows": rows}
    (OUT / "epl_latest.json").write_text(json.dumps(latest, indent=2), encoding="utf-8")
    print(f"events={len(events)} normalized_rows={len(rows)} raw={raw_path}")

if __name__ == "__main__":
    main()
