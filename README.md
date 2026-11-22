# RAMI CHESS COACH AI

A personal chess-training data pipeline for Lichess account `rami9191`.

## Data preservation

- The original 50-game PGN baseline must remain immutable.
- Newly synchronized games must be stored separately and deduplicated by Lichess game ID.
- Baseline statistics and incremental statistics must remain distinguishable.
- Never overwrite or delete historical games or training records.

## Automated synchronization

A GitHub Actions workflow is configured to fetch public Lichess games for `rami9191` and append only unseen game IDs. Public-game retrieval requires no password or API token. The original baseline PGN and baseline statistics remain separate.

## Training objective

Track openings and defenses by color, recurring strengths and weaknesses, training-plan changes, and progress toward 1800 Rapid.

## Current status

Repository initialized. The original baseline PGN remains separate and immutable (not uploaded). All 50 baseline Lichess game IDs are seeded in `data/sync_state.json` so the incremental sync can skip overlapping baseline games. Incremental sync status at the latest confirmed run: 0 new games.
