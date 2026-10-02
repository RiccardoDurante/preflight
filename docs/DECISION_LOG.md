# PreFlight — Decision Log

A running log of the key decisions I made while building the MVP. For each
one I record the context, the options I considered, the choice I made, and
the reason behind it.

The point is not to show that every choice was perfect, but to show that
every choice was **conscious**.

---

## D1 — Scope: what to build, what to cut

**Date:** early planning phase
**Context:** the original idea had two parts: preventing metadata errors
before release (upstream), and detecting unclaimed royalties in existing
catalogs (downstream). Both were valuable, but building both would have
taken months.

**Options considered:**
- A. Build both, small versions of each.
- B. Build only the upstream tool (prevention).
- C. Build only the downstream tool (detection).

**Choice:** B — only the upstream tool.

**Reason:** the upstream angle is less crowded (most existing tools are
downstream) and it can be built without accessing any licensed dataset,
which was a hard constraint for a solo project. The downstream angle can
become v2 later.

---

## D2 — Framework: Flask vs Django vs FastAPI

**Context:** I needed a Python web framework I could learn quickly.

**Options:**
- Flask: simple, close to what CS50 teaches, minimal boilerplate.
- Django: more complete but heavier, with an ORM and admin panel.
- FastAPI: modern and async, but more focused on APIs than on HTML apps.

**Choice:** Flask.

**Reason:** I needed a full web app with HTML pages, not just an API, and I
wanted the simplest thing that could work. Flask is the natural fit for an
MVP at this scale, and it's what CS50 used.

---

## D3 — Database: SQLite vs PostgreSQL

**Context:** I needed to persist analyzed tracks and their issues.

**Options:**
- SQLite: single file, no server, no setup.
- PostgreSQL: production-grade, but requires installation and
  configuration.

**Choice:** SQLite.

**Reason:** for an MVP that runs locally, SQLite is enough. The application
code doesn't change if I switch to PostgreSQL later — only the connection
string does. This is a deferred decision, not a compromise.

---

## D4 — Data structure: separate issues table vs JSON field

**Context:** each analyzed track has a variable number of issues attached.
I could store them as JSON inside the tracks row, or in a separate
issues table.

**Options:**
- A. JSON field in tracks: simpler, fewer joins.
- B. Separate issues table with foreign key: relational, queryable.

**Choice:** B — separate table.

**Reason:** I wanted to be able to ask questions **across issues**, for
example "what is the most common error in all analyzed tracks?" That
question is trivial with a proper table and impossible with JSON blobs.
The extra complexity is worth the flexibility.

---

## D5 — PDF library: WeasyPrint vs xhtml2pdf

**Context:** I wanted to export reports as PDFs.

**Options:**
- WeasyPrint: better output quality, but requires GTK system libraries.
- xhtml2pdf: pure Python, works on Windows out of the box, simpler output.

**Choice:** xhtml2pdf.

**Reason:** I tried WeasyPrint first and hit a wall — it fails to install
cleanly on Windows without extra system dependencies. xhtml2pdf worked
immediately and its output quality is good enough for the MVP. Fighting a
library is time not spent on the product.

---

## D6 — PDF template: reuse vs separate

**Context:** the browser report uses Bootstrap and custom CSS. xhtml2pdf
doesn't support Bootstrap well.

**Options:**
- A. Try to make one template work for both browser and PDF.
- B. Create a second, simpler template just for the PDF.

**Choice:** B — separate templates.

**Reason:** one template trying to serve two very different rendering
engines would have meant constant compromises on both sides. Two focused
templates are easier to maintain and let each output look its best.

---

## D7 — Score calibration: simple weights vs per-rule weights

**Context:** the Risk Score needs to reflect how "bad" a track is. I could
assign the same weight to every red issue, or give each rule its own
weight based on economic impact.

**Options:**
- A. Simple: -20 for each red, -8 for each amber.
- B. Per-rule weights (e.g., splits sum different from 100 -> -40, malformed
  ISRC -> -25, etc.), calibrated on real royalty loss data.

**Choice:** A for the MVP, with B on the roadmap.

**Reason:** per-rule weights require data I don't have yet on the average
economic impact of each error type. A simple approach is honest and
transparent. I document this as a known limitation in the README so it
doesn't look like an oversight.

---

## D8 — Style of the code: idiomatic Python vs beginner-friendly

**Context:** the project uses AI-assisted coding. The AI's default output
tends to be idiomatic and dense (list comprehensions, zip, compiled
regexes at module level, etc.).

**Options:**
- A. Keep the idiomatic style — more concise.
- B. Rewrite in a more beginner-friendly style — closer to what a CS50
  student would produce, easier to explain line by line.

**Choice:** B.

**Reason:** the value of the project is not in showing off Python tricks.
It's in demonstrating I understand the ideas and can defend every line.
Simple code that I can explain 100% is worth more than clever code I'd
struggle to justify in an interview.

---

## D9 — Use of AI: disclose vs hide

**Context:** I used Claude as a coding tutor throughout the project.

**Options:**
- A. Don't mention it. Present the project as if written from scratch.
- B. Add an "Use of AI" section to the README explaining how the AI was
  used and what decisions were mine.

**Choice:** B — full disclosure.

**Reason:** CS50 explicitly allows external AI tools when used as a tutor.
Honesty is a safer position than pretending: the code style would give it
away anyway to an attentive reviewer, and disclosing shows maturity in
managing the tool. For future employers, honesty about tooling is a
strength, not a weakness.

---

## D10 — Branding: what to call it

**Context:** the working title was "Metadata Risk Detector," which is
descriptive but forgettable.

**Options I considered:** MetaGuard, RoyaltyShield, BlackBox Prevention,
Metaboxx, PreFlight.

**Choice:** PreFlight.

**Reason:** the "preflight check" metaphor (like an aviation checklist
before takeoff) is instantly understood by product people in music tech
and clearly captures what the tool does. It's short, memorable, and B2B in
tone.

---

## D11 — Branching strategy for v2 development

**Context:** `main` is the exact commit already submitted, certified, and
linked publicly on LinkedIn. Phase 2 introduces new dependencies and a new
external integration, with no guarantee everything would work on the first
try.

**Options:**
- A. Keep committing directly to `main`.
- B. Tag the current commit as a fixed reference point, then create a
  separate `v2` branch for all new work, leaving `main` untouched.

**Choice:** B.

**Reason:** the tag (`v1.0-cs50`) gives a permanent, citable reference to
the exact CS50 submission. The `v2` branch lets me experiment freely
without risking the version that is already public and graded. GitHub
shows `main` by default to anyone following the LinkedIn link, so nothing
changes for existing viewers until I choose to merge.

---

## D12 — Handling MusicBrainz network failures

**Context:** `check_isrc_conflict` depends on an external API call, unlike
every other rule, which is instant and offline. A network failure (no
internet, MusicBrainz down) needed a defined behavior.

**Options:**
- A. Fail silently: treat a network error the same as "no conflict found."
  The user never notices the check didn't run.
- B. Surface it as a distinct, low-severity issue ("Could not check
  MusicBrainz for ISRC conflicts right now"), using a new "info" severity
  that does not affect the Risk Score.

**Choice:** B.

**Reason:** for a tool whose whole point is catching problems before
release, silently skipping a check is worse than admitting it couldn't run.
An "info" issue costs nothing in score but keeps the user honestly informed.

---

## D13 — Cache expiry policy for MusicBrainz lookups

**Context:** the `mb_cache` table stores every ISRC lookup result, to avoid
re-querying MusicBrainz and to respect its 1 req/sec limit.

**Options:**
- A. No expiry: once an ISRC is looked up, the result is reused forever.
- B. Add a time-to-live (e.g., re-check after 30 days).

**Choice:** A, for now.

**Reason:** the data MusicBrainz holds for a given ISRC (title, artist)
rarely changes after the fact. A TTL adds complexity for a benefit that
doesn't apply to this use case yet. If real usage shows otherwise, this is
a small, isolated change to `get_cached_mb_result`.

---

## D14 — Fuzzy matching thresholds and ISWC scope

**Context:** Phase 2 needed two separate similarity checks: (1) is a
MusicBrainz artist name close enough to the track's artist to count as
"the same person," and (2) are two writers on the same track close enough
to be a spelling variant of one person. It also needed a decision on
whether to search MusicBrainz by ISWC as well as ISRC in this phase.

**Options:**
- Single shared similarity threshold for both checks, vs. two separate
  thresholds tuned to each case.
- Implement both ISRC and ISWC conflict search now, vs. ISRC only.

**Choice:** two separate thresholds (70 for the MusicBrainz artist check,
60 for the writer-duplicate check), and ISRC only for this phase.

**Reason:** the two checks compare different things. Matching a track's
artist against MusicBrainz mostly needs to tolerate small spelling
differences, so 70 works well. Matching two writer names on the same track
needs to also catch heavy abbreviations like "M. Rossi" vs "Mario Rossi",
which share fewer characters, so a lower threshold (60) is needed to catch
them — accepting a slightly higher chance of a false positive between two
different people with similar names. ISWC search uses a different
MusicBrainz endpoint (`work`, not `recording`); scoping it out kept this
phase focused and testable. It is a natural, self-contained addition for a
later phase. (Update: implemented in D16.)

---

## D15 — Testing an external API without calling it

**Context:** `check_isrc_conflict` calls a real external API and reads from
the database. Tests that hit the real network would be slow, flaky (depend
on MusicBrainz being reachable), and could pollute `database.db` with test
data.

**Options:**
- A. Let tests call the real MusicBrainz API and the real database.
- B. Use pytest's built-in `monkeypatch` fixture to temporarily replace
  `models.get_cached_mb_result`, `models.save_mb_result`, and
  `musicbrainz_client.search_recordings_by_isrc` with fake functions during
  each test, restored automatically afterwards.

**Choice:** B.

**Reason:** the new tests run in 0.25 seconds total (27 tests, including
the 18 from Phase 1) with zero network calls, and their outcome no longer
depends on MusicBrainz being online. This is standard practice for testing
any code with an external dependency, and it kept the existing tests'
plain, explicit style — no new library was needed, `monkeypatch` is
already part of pytest.

---

## D16 — Adding ISWC conflict search after all

**Context:** D14 deliberately scoped ISWC search out of Phase 2, to keep
the phase small and testable. After finishing Phase 2 and its cleanup, I
decided to come back and add it, using the same pattern already proven for
ISRC (a client function, a cache table, a validation rule, mocked tests).

**Options:**
- A. Leave it as a future phase, as originally planned.
- B. Implement it now, re-using the exact same pattern as the ISRC
  conflict check, now that the pattern is proven and tested.

**Choice:** B.

**Reason:** the ISRC conflict check (client function + cache table +
validation rule + mocked tests) turned out to be a reusable template. The
ISWC version needed one real difference, not just a copy-paste: a
recording has one main artist, but a work (composition) can have several
writers, so `check_iswc_conflict` compares the *whole* writers list
against MusicBrainz's composer list, and treats a match on any single pair
as "the same work" — not a conflict. This mirrors how real-world
co-written songs work, and reuses `ARTIST_SIMILARITY_THRESHOLD` from D14
for consistency, since both checks answer the same underlying question:
"is this close enough to count as the same person?"

---

## D17 -- Economic impact model: aggregate risk fraction vs per-issue cost attribution

**Context:** Phase 3 (ROADMAP) originally planned a formula with four
factors -- estimated streams, a per-stream rate, an "uncollected share," and
a "territory factor" -- producing a cost estimate for *each individual
issue* ("this issue may cost you approximately X euro/year"). Building
that would require real-world data on how much revenue each specific type
of error actually blocks, which isn't publicly available (the same gap
already noted in D7 for the Risk Score weights).

**Options considered:**
- A. Research and assign a distinct euro-cost weight to each of the ten
  validation rules, matching the original per-issue formula.
- B. Reuse the existing severity weights from the Risk Score (red = heavier,
  amber = lighter, from D7) as a single "risk fraction" of total revenue,
  and apply it against total estimated revenue (streams x per-stream
  royalty rate, varying by territory) to get one aggregate euro figure per
  track.

**Choice:** B.

**Reason:** the same data gap that forced a simple, transparent Risk Score
in D7 applies here -- there is no public source for issue-specific euro
impact, so inventing per-rule weights would trade one honest approximation
for a more precise-*looking* but equally unfounded one. Reusing the Risk
Score's severity weights (red = 15% of revenue at risk, amber = 5%, capped
at 80% so there's always some chance revenue still comes through) keeps the
two numbers -- the 0-100 score and the euro estimate -- telling the same
story instead of two inconsistent ones. Per-stream royalty rates do vary by
territory (Italy, USA, other), so that part of the original formula is
implemented as specified. The per-issue breakdown and a dedicated
methodology document remain a future refinement if real impact data
becomes available.

---

## D18 -- CSV format for batch upload: numbered columns vs a single delimited cell

**Context:** Phase 4 needed a CSV format that could represent a variable
number of writers per track (one track might have one writer, another
three), using a format a label or distributor could actually produce from
a spreadsheet.

**Options considered:**
- A. One "writers" column per row, with a custom delimiter inside the cell
  (e.g. `Mario Rossi:60:00123456789;Anna Bianchi:40:`).
- B. Numbered columns -- `writer1_name`, `writer1_split`, `writer1_ipi`,
  `writer2_name`, and so on -- with each row using as many as it needs.
- C. One row per writer instead of one row per track, with a shared track
  ID column to group them back together.

**Choice:** B.

**Reason:** option A is compact but fragile -- it asks the person
preparing the CSV to hand-write a custom mini-syntax inside a single
Excel cell, which is exactly the kind of manual, error-prone step this
whole tool exists to catch. Option C is the most "correct" relationally,
but it changes what a "row" means in a way that doesn't match how a
distributor's spreadsheet is usually shaped (one line per track). Option B
reads naturally in a spreadsheet -- each writer gets its own three columns,
filled in or left blank -- and `parse_batch_row` (`batch.py`) handles a
different writer count per row with a simple `while f"writer{i}_name" in
row` loop, so there's no fixed maximum to document or enforce.

---

## D19 -- Defining "most frequent issue" for the dashboard: by message vs by fix

**Context:** the dashboard needs to show which problem shows up most often
across a catalog. Each issue has a `message` (which often embeds per-track
data, like a writer''s name or a specific percentage) and a `fix` (a static
recommendation that never changes between tracks for the same rule).

**Options considered:**
- A. Group and count by `message`. Simple, but two tracks with "the same"
  problem (e.g. two different tracks both missing a publisher) would
  almost never produce an identical string once any rule embeds dynamic
  data, making the count meaningless for several rules.
- B. Group and count by `fix`. Every rule''s fix text is a fixed string per
  branch (see checks.py), so it is stable across tracks and makes a
  meaningful aggregate.

**Choice:** B.

**Reason:** the dashboard''s purpose is to tell someone managing a catalog
"what should I go fix first," and the fix text already answers that
question directly -- counting by fix means the number on screen is also
the actionable recommendation, with no translation needed. Grouping by
`message` would have under-counted real duplicates and over-fragmented
the list for no benefit.

---

## D20 -- Hosting choice and accepting ephemeral storage for the demo

**Context:** the project needed a live deployment to be useful as a
portfolio piece -- a repository alone asks a reviewer to clone and run it
locally, which most people won''t do. This also surfaced a real problem:
`requirements.txt` had been generated with `pip freeze` and captured the
entire local virtualenv, including CS50 tooling (`lib50`, `submit50`,
`style50`) and a Windows-only package (`python-magic-bin`) that would have
failed to install on Render''s Linux build.

**Options considered:**
- A. Render free tier, accepting its ephemeral filesystem (SQLite data is
  wiped on redeploy or after the service sleeps from inactivity).
- B. A host with persistent storage from the start (a paid Render disk,
  Railway with a volume, or migrating to a hosted Postgres database).

**Choice:** A, with the limitation documented plainly in the README rather
than hidden or worked around.

**Reason:** the live deployment''s job is to let someone try the validation
engine, the batch upload, and the dashboard -- not to act as a real,
persistent catalog for anyone''s actual music. Paying for persistence, or
migrating to Postgres, would be solving a problem the demo doesn''t have
yet. This is the same reasoning already applied in D3 (SQLite over
Postgres) and D7 (simple score over unfounded precision): don''t add
complexity for a need that hasn''t materialized. If the project later gets
a real user who needs their data to persist, that is exactly the trigger
for Phase 5''s move to Postgres -- not a reason to pre-build it now.
Separately, trimming `requirements.txt` down to the project''s actual
direct dependencies (Flask, requests, RapidFuzz, xhtml2pdf, pytest, plus
`gunicorn` for production) was not just a cleanup: it was necessary for
the Linux build to succeed at all.

---

## Meta-principle

Every entry above follows the same structure: **context -> options -> choice
-> reason.** This is deliberate. When I look back at the project in six
months, or when someone else reviews it, the "why" of every decision is
recoverable in one place.

For an early-career project manager, the ability to make and document
decisions is more important than the ability to write clever code.




