# PreFlight — Roadmap

This document tracks what has been built (v1.0, the current MVP) and what
could come next in future phases. Each phase lists its goals, main
deliverables, an effort estimate, and its main dependencies.

## Phase 1 — MVP (v1.0) — COMPLETED

**Goal:** validate the idea end-to-end with a working prototype that a
non-technical person can actually use.

**Deliverables:**
- Web app with input form, validation engine, result report, and history.
- Seven validation rules covering the most common metadata errors.
- Risk Score (0–100) with three severity bands.
- PDF export of the report.
- Automated tests (18 tests, all passing).
- Documentation: README, product brief, decision log, roadmap.

**Effort:** ~40 hours over 3 weeks, part-time.

**Dependencies:** none. Fully self-contained MVP.

**Status:** shipped as the CS50 Final Project.

---

## Phase 2 — External data integration (v1.1) — COMPLETED

**Goal:** move from a self-contained engine to a tool that checks metadata
against a real-world dataset.

**Deliverables:**
- Integration with **MusicBrainz** REST API (free, no auth needed) for
  ISRC/ISWC lookups and duplicate detection.
- Caching layer (SQLite) to respect MusicBrainz's 1 req/sec limit.
- New validation rule: "This ISRC is already registered to a different
  work — potential conflict."
- Fuzzy matching on writer names using ``rapidfuzz`` (catches "Mario Rossi"
  vs "M. Rossi").
- ISWC conflict search (same pattern as ISRC, extended to works/composers).

**Effort estimate:** ~20 hours.

**Dependencies:** MusicBrainz service availability. No paid access needed.

**Success metric:** at least 30% of test tracks receive at least one
additional validation signal from MusicBrainz.

**Status:** shipped on branch `v2` (34/34 tests passing). ISWC lookup was
initially scoped out (see DECISION_LOG D14) and added afterwards in the
same phase (see DECISION_LOG D16). Still pending merge to `main`.

---

## Phase 3 — Economic impact estimation (v1.2)

**Goal:** turn each issue from a warning into a monetary estimate. This is
what makes the tool interesting to a distributor or a label.

**Deliverables:**
- Transparent formula: ``estimated_streams x per-stream-rate x
  uncollected-share x territory-factor``.
- Public methodology document (parameters, assumptions, sources).
- Per-issue estimate shown in the report: "This issue may cost you
  approximately X euro/year in lost royalties."
- Aggregate estimate at the top of the report.

**Effort estimate:** ~15 hours (mostly research, not code).

**Dependencies:** publicly available per-stream royalty rates and market
average data.

**Success metric:** estimates fall within a plausible order of magnitude
compared to industry reports (Notes.fm averages ~$15.5k/artist).

**Status:** shipped on branch `v2`, with a simpler model than originally
planned (see DECISION_LOG D17). The report now shows, per track: total
estimated revenue (streams x per-stream rate by territory), the percentage
of that revenue at risk (derived from the same severity weights used for
the Risk Score), and the resulting euro amount at risk. This replaces the
originally planned `uncollected-share x territory-factor` formula and the
per-issue cost breakdown -- both deferred, see D17. `expected_streams`
input is also validated (non-numeric or negative values are flagged as an
issue, consistent with how every other field is checked).

---

## Phase 4 — Batch analysis and CSV upload (v1.3)

**Goal:** move from single-track analysis to catalog-wide scanning, which
is how a distributor or a label would actually use the tool.

**Deliverables:**
- CSV upload (compatible with common distributor export formats).
- Batch processing with progress indicator.
- Catalog-level dashboard: distribution of scores, most frequent issues,
  total money at risk.
- CSV export of the results.

**Effort estimate:** ~25 hours.

**Dependencies:** none. Builds on top of the existing engine.

**Success metric:** processing 1,000 tracks in under 60 seconds on a
standard laptop.

**Status:** CSV upload and batch analysis shipped on branch `v2` (see
DECISION_LOG D18 for the CSV format decision). Each row is validated,
analyzed with the same engine as the single-track form, and saved to the
database; the results page lists every track with its score, issue count,
and revenue at risk, linking to each full report. Rows with a missing
title or artist are skipped with a visible reason instead of failing the
whole upload. The catalog-level dashboard (score distribution, most
frequent issues, total money at risk) is not built yet -- it is the
natural next step, since the history page already has all the per-track
data it would need to aggregate.

---

## Phase 5 — API and multi-tenant (v2.0)

**Goal:** make PreFlight consumable as a service, not just as a web app.
This is the phase that would allow real integration with a distributor's
ingestion pipeline.

**Deliverables:**
- REST API with authentication (API keys).
- Multi-tenant architecture (each customer has an isolated catalog).
- Rate limiting and usage tracking.
- Migration from SQLite to PostgreSQL.
- Basic admin panel for customers.

**Effort estimate:** ~60 hours.

**Dependencies:** first design partner interested in integrating.

**Success metric:** at least one distributor or CMO using the API in a
pilot.

---

## Out of scope for the foreseeable future

- Direct integration with SIAE, ASCAP, MLC registries. This requires
  licensed partnerships that go far beyond a solo project. In a full
  business case this would be Phase 6+, after commercial validation.
- Machine-learning-based error detection. The current rule-based approach
  covers 80% of the value with 5% of the complexity.
- End-user marketplace or subscription billing. Would come only after B2B
  traction is established.

---

## Guiding principles for future work

1. **Ship the smallest useful thing first.** Every phase must deliver
   something real, not a "half feature."
2. **Document decisions.** See DECISION_LOG.md for how choices are recorded.
3. **Be honest about limits.** Every phase's README section states clearly
   what is not covered.
4. **Prefer transparent formulas over black-box models.** For a tool that
   claims to fight opacity, opacity in the tool itself would be a
   contradiction.


