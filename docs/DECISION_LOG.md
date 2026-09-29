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

## Meta-principle

Every entry above follows the same structure: **context -> options -> choice
-> reason.** This is deliberate. When I look back at the project in six
months, or when someone else reviews it, the "why" of every decision is
recoverable in one place.

For an early-career project manager, the ability to make and document
decisions is more important than the ability to write clever code.
