# Conference Tracker & AI Conference Pulse

This dashboard ships with two complementary conference features. Both are
driven by a single config file: [`data/conferences.json`](../data/conferences.json).

| Section | What it shows | Driven by |
| --- | --- | --- |
| 📍 **Amsterdam AI Conference Tracker** | A fictional planning slate of upcoming local events. Useful for roadmap launches, field marketing, and local community moments. | `fictional_local_slate` |
| 🧠 **AI Conference Pulse** | Real-world AI conferences (NeurIPS, ICLR, re:Invent, …) that are being talked about in *today's* article pool. | `major_ai_conferences` |

The schema for both sections lives in [`data/conferences.schema.json`](../data/conferences.schema.json).

---

## How the local tracker works

For each entry in `fictional_local_slate`, the generator builds a concrete date
range for the current year using `month` / `day` / `duration_days`. Past events
are filtered out so the dashboard always shows what's coming up. When every
event for the year has already passed, the schedule automatically rolls forward
to next year.

### Adding a new local event

1. Open [`data/conferences.json`](../data/conferences.json).
2. Add a new object to `fictional_local_slate`:

   ```json
   {
     "name": "Your Event Name",
     "month": 6,
     "day": 15,
     "duration_days": 2,
     "venue": "Venue name",
     "focus": "What the event is about",
     "format": "Conference / Meetup / Summit / Workshop",
     "audience": "Who attends",
     "miro_angle": "How Miro should show up there",
     "watch_for": "Signals to watch for in coverage",
     "tags": ["Topic1", "Topic2"]
   }
   ```

3. (Optional) Re-run `python3 eng_brand_machine.py` locally to preview, or just
   open a PR — the GitHub Action regenerates `index.html` automatically.

### Changing the city

Update `default_location` in `data/conferences.json`. Everything in the local
tracker (heading, callouts, "Default Location" stat) follows automatically.

---

## How the AI Conference Pulse works

The Pulse panel performs a lightweight keyword scan over every article fetched
in the run — Hacker News, dev.to, GitHub trending, Reddit, and ~40 RSS feeds.

For each entry in `major_ai_conferences`:

1. Lowercase the article's `title + description + source`.
2. Match against the conference's `keywords` array (substring match, case
   insensitive).
3. Collect the matches, sort by score, and surface the top N (default: 4) on
   the dashboard.

Conferences with **zero matches** are hidden. If *nothing* matches, the panel
shows an empty-state hint pointing reviewers at `data/conferences.json`.

### Adding a conference to the Pulse

```json
{
  "name": "Short Name",
  "long_name": "Full conference name",
  "keywords": ["short-name", "full conference name"],
  "cadence": "Annual · Month",
  "audience": "Who tends to attend",
  "miro_angle": "How Miro should show up alongside coverage",
  "signal_topics": ["topic-a", "topic-b"]
}
```

Tips:

- **Keywords are substring matches.** Add a couple of variations
  (e.g. `"re:invent"`, `"reinvent"`) so casual mentions still get caught.
- Avoid keywords that overlap with common English words ("ai", "cloud", …) —
  they'll trigger false positives.
- `signal_topics` is purely cosmetic but helps reviewers decide whether a
  conference deserves a Miro response.

### Testing your changes

```bash
python3 -m unittest tests.test_conferences -v
python3 scripts/list_conferences.py --type all --format json
python3 eng_brand_machine.py
open index.html
```

---

## CLI helper

`scripts/list_conferences.py` reads `data/conferences.json` without running the
full pipeline. It's handy for:

- Cross-posting upcoming events to Slack (`--format json | jq …`).
- Validating that the JSON parses (`--type all`).
- Showing the schedule for a different city without editing the file
  (`--location "Berlin, Germany"`).

---

## File map

```text
data/
├── conferences.json          # The catalog editors actually touch
└── conferences.schema.json   # JSON schema for editor validation

scripts/
└── list_conferences.py       # CLI surface over the catalog

tests/
└── test_conferences.py       # Unit tests for the loader, scheduler, and pulse

docs/
└── CONFERENCE_TRACKER.md     # This file
```
