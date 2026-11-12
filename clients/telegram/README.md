# goSpot Telegram client (imported prototype)

A Telegram bot for plane spotters: pick an airport, get the next hour of arrivals, see which aircraft are new to your logbook, set up a live radar and ATC audio, get spotting locations. It runs either locally (`bot.py`, long polling) or on AWS (three Lambda functions behind an API Gateway webhook, DynamoDB for users and aircraft, the bot token in SSM Parameter Store).

## Provenance, please read

This is **my own prototype, built before the Qodo hackathon started (2 Nov 2026)** and imported into this repository in a single commit so the git history shows what is old and what was changed during the event. The `gospot` core library in `src/` was written during the event; the plan is that this client becomes a thin layer on top of it.

Edits made on import (everything else is unchanged):

- A hard-coded real person (name and JetPhotos id used as the default demo account) was removed. The demo now uses synthetic sample aircraft from `aws_lambda/demo_aircraft.json`.
- Scraped data was **not** imported: the bundled gallery JSON and the SpotterGuide index.
- The FlightRadar24 client was **not** imported (unofficial endpoint, browser User-Agent). Flight data now comes through `aws_lambda/schedule_provider.py`; with no provider configured the bot answers "could not fetch the schedule".
- The JetPhotos scraping code was kept, but behind `aws_lambda/polite_http.py` (see below). Browser impersonation was removed everywhere, including the Wikipedia calls.
- IAM policy files (they contain an AWS account id) and the token-in-environment script were left out; `deploy_to_aws.sh` was rewritten.
- The Mini App address is now one constant, `HUB_BASE_URL` in `aws_lambda/i18n.py`, overridable with the environment variable of the same name.

## Scraping is off by default

`aws_lambda/polite_http.py` is the only way the code touches third-party sites that offer no API. With `SCRAPING_ENABLED=1` it sends an honest User-Agent (`goSpot/0.1 (+repo URL)`), reads and obeys `robots.txt` (and refuses to scrape if the honest client is refused), and spaces requests per host. It stores nothing. If a site blocks the honest client, the answer is to stop, not to disguise it. You are responsible for reading each site's terms before enabling it.

## Run and test

```bash
# from this folder
cp .env.example .env            # put your bot token there (git-ignored)
python3 bot.py                  # local polling mode
../../.venv/bin/pytest -q       # client tests (run from this folder; they use relative paths)
```

Deployment is manual from the maintainer's machine: `./deploy_to_aws.sh` (add `--store-token` once to put the token into SSM without it touching a command line). There is deliberately no deployment workflow in CI (AGENTS.md, "Boundaries").

## Known gaps (backlog)

- No flight-data provider yet (an open ADS-B based one is the obvious first).
- "New to me" should read the goSpot logbook instead of the old gallery import.
- `datetime.utcnow()` is deprecated in the legacy code.
- Sharing must follow AGENTS.md rule 2 (explicit action by the spotter) everywhere the bot sends sighting data.
