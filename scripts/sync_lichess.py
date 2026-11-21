#!/usr/bin/env python3
"""Incrementally export public Lichess games without modifying the baseline."""
import json, os, re, time, urllib.request
from pathlib import Path
from datetime import datetime, timezone

USERNAME = os.environ.get("LICHESS_USERNAME", "rami9191")
BASE = Path("data")
PGN_PATH, STATE_PATH, STATS_PATH = BASE/"new_games.pgn", BASE/"sync_state.json", BASE/"new_games_stats.json"
API = f"https://lichess.org/api/games/user/{USERNAME}"

def split_games(pgn):
    chunks = re.split(r"(?=^\[Event )", pgn, flags=re.MULTILINE)
    return [c.strip() for c in chunks if c.strip() and "[Event " in c]

def headers(game):
    return dict(re.findall(r'^\[([A-Za-z0-9_]+) "(.*)"\]$', game, flags=re.MULTILINE))

def game_id(h):
    match = re.search(r"lichess\.org/([A-Za-z0-9]{8})", h.get("Site", ""))
    return match.group(1) if match else None

def main():
    BASE.mkdir(exist_ok=True)
    if STATE_PATH.exists():
        state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    else:
        start = datetime(2026, 11, 21, tzinfo=timezone.utc)
        state = {"username": USERNAME, "last_sync_ms": int(start.timestamp()*1000), "known_game_ids": []}
    known = set(state.get("known_game_ids", []))
    old_pgn = PGN_PATH.read_text(encoding="utf-8") if PGN_PATH.exists() else ""
    for old in split_games(old_pgn):
        gid = game_id(headers(old))
        if gid:
            known.add(gid)

    # A 48-hour overlap handles delayed exports; game IDs prevent duplicates.
    since = max(0, int(state["last_sync_ms"]) - 48*60*60*1000)
    url = API + f"?since={since}&max=300&opening=true"
    request = urllib.request.Request(url, headers={
        "Accept": "application/x-chess-pgn",
        "User-Agent": "RAMI-CHESS-COACH-AI/1.0"
    })
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = response.read().decode("utf-8", errors="replace")

    additions = []
    for game in split_games(payload):
        gid = game_id(headers(game))
        if gid and gid not in known:
            additions.append(game)
            known.add(gid)

    if additions:
        with PGN_PATH.open("a", encoding="utf-8") as output:
            if old_pgn and not old_pgn.endswith("\n"):
                output.write("\n")
            output.write("\n\n".join(additions) + "\n")

    all_games = split_games(PGN_PATH.read_text(encoding="utf-8")) if PGN_PATH.exists() else []
    stats = {
        "username": USERNAME,
        "scope": "incremental games only; baseline is separate",
        "games_total": 0, "wins": 0, "draws": 0, "losses": 0,
        "by_color": {
            "white": {"wins": 0, "draws": 0, "losses": 0},
            "black": {"wins": 0, "draws": 0, "losses": 0}
        },
        "openings_by_color": {"white": {}, "black": {}},
        "last_updated_utc": datetime.now(timezone.utc).isoformat()
    }
    for game in all_games:
        h = headers(game)
        color = ("white" if h.get("White", "").lower() == USERNAME.lower()
                 else "black" if h.get("Black", "").lower() == USERNAME.lower() else None)
        if not color:
            continue
        stats["games_total"] += 1
        result = h.get("Result", "*")
        outcome = (
            "wins" if (result == "1-0" and color == "white") or (result == "0-1" and color == "black")
            else "losses" if result in ("1-0", "0-1")
            else "draws" if result == "1/2-1/2" else None
        )
        if outcome:
            stats[outcome] += 1
            stats["by_color"][color][outcome] += 1
        opening = h.get("Opening", h.get("ECO", "Unknown"))
        bucket = stats["openings_by_color"][color]
        bucket[opening] = bucket.get(opening, 0) + 1

    state.update({
        "username": USERNAME,
        "known_game_ids": sorted(known),
        "last_sync_ms": int(time.time()*1000),
        "last_sync_utc": datetime.now(timezone.utc).isoformat(),
        "last_added_count": len(additions)
    })
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    STATS_PATH.write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Added {len(additions)} new games; incremental archive contains {len(all_games)} games.")

if __name__ == "__main__":
    main()
