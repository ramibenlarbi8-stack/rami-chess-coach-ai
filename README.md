# RAMI CHESS COACH AI

A personal chess-training data pipeline for Lichess account `rami9191`.

## Data preservation

- The original 50-game PGN baseline must remain immutable.
- Newly synchronized games are stored separately in `data/new_games.pgn` and deduplicated by Lichess game ID.
- Baseline statistics and incremental statistics remain distinguishable.
- Never overwrite or delete historical games or training records.

## Automated synchronization

A GitHub Actions workflow fetches public Lichess games for `rami9191` and appends only unseen game IDs. Public-game retrieval requires no password or API token.

## Training objective

Track openings and defenses by color, recurring strengths and weaknesses, training-plan changes, and progress toward 1800 Rapid.

## Current status — 2026-11-24

- Immutable baseline: 50 games (original PGN remains separate and was not uploaded).
- Incremental archive: 3 games, all wins (2 White, 1 Black).
- Total tracked game IDs: 53 (50 baseline IDs + 3 incremental IDs).
- Incremental openings: White — Ruy Lopez: Steinitz Defense (1), French Defense: Exchange Variation (1); Black — Pirc Defense (1).
- Last verified GitHub Actions sync: 2026-11-24 18:30 UTC; API fetch completed successfully and found 0 additional games.
- The three Nov 24 games are archived separately; see `training/2026-11-24-review.md` for coaching review.
