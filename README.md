# EDGE FC — Soccer Betting Intelligence

Market-anchored soccer analysis pipeline.

## Phase 1
- Fetch EPL events from The Odds API
- Snapshot FanDuel, DraftKings, and Fanatics markets
- Preserve timestamped raw responses
- Normalize available markets for EDGE FC analysis
- Keep credentials in GitHub Actions secrets only

## Run
Use **EDGE FC Odds Fetch** under Actions. Required repository secret: `ODDS_API_KEY`.

Initial sport: `soccer_epl`

Outputs are written to `data/odds/`.
