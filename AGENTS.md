# AGENTS.md

Instructions for coding agents and reviewers working on goSpot.

## What this project is

goSpot is a plane spotter's logbook and session planner. A spotter logs sightings and is told straight away whether an aircraft is new to them. The core is a small Python library with a CLI (`gospot`); a web page and Telegram messages are planned as thin clients on top of the same core.

## Set up and check your work

```bash
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
.venv/bin/pytest                      # must pass before you report a task done
.venv/bin/gospot log sp-exe --at WAW  # quick manual check; use GOSPOT_DB=/tmp/x.db to avoid touching real data
```

Layout: `src/gospot/registration.py` (registration parsing), `logbook.py` (SQLite logbook), `cli.py` (command line), `tests/` (one test file per module).

## Project rules

Each rule says where it applies and why it exists. The reasons come from real review findings, so please keep them in mind rather than working around them.

1. **Registrations go through `parse_registration`.**
   *Applies to:* any code that accepts, stores, compares or prints an aircraft registration.
   *Why:* the canonical form (`SP-EXE`) is the logbook key. Raw text let `banana` pass as `B-ANANA`, and a Unicode `ſ` fold into `S`. Never store or compare the user's raw string.

2. **Sighting data is private by default.**
   *Applies to:* anything that creates, exports or logs the logbook: files are `0600`, new directories `0700`, nothing is sent to a third party.
   *Why:* a logbook records where and when someone spots. Qodo found the first version readable by other local users.

3. **Expected failures are one-line errors, never tracebacks.**
   *Applies to:* every boundary a user touches: the CLI (`error: ...`, exit code 2) and, later, web and Telegram handlers (a short reply).
   *Why:* an unusable `--db` path crashed with a traceback because the logbook was opened outside the error handling.

4. **Times are timezone-aware UTC, to the minute.**
   *Applies to:* the logbook and every parser that produces a time. Naive times are rejected; up to five minutes in the future is allowed for phone clock drift.
   *Why:* sightings from different time zones must compare correctly, and the duplicate rule works on the minute.

5. **Behaviour, tests and docs change together.**
   *Applies to:* every PR that changes what the code does.
   *Why:* the README once said future times were rejected while the code allowed five minutes. A change without its test and doc update is not finished.

## Definition of done (quality gate)

A task is done only when all of this holds; otherwise report it as **not done** and say what blocks it.

- `.venv/bin/pytest` passes.
- Qodo has reviewed the change: `qodo review` on uncommitted work, or the Review Resolver on a PR. For a PR, the latest completed review covers the current head commit.
- Every valid **High** and **Medium** finding, including Medium bugs, is fixed. Findings you disagree with are listed with evidence.
- **Low** findings are not required to be fixed but are always reported to the maintainer.
- Review is rerun after fixes until the gate is met. If a pass repeats the same concern without progress, stop and ask.

## Boundaries

- Deployment happens only from the maintainer's own machine. Do not add deployment or release workflows to this repository.
- Never commit credentials, bot tokens, `.env` files, or scraped third-party data (for example photo databases). Use synthetic fixtures in tests.
- Keep pull requests small and focused on one change. The repository is public.
- Say in the PR when AI assistance was used.
