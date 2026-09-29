# PreFlight — Product Brief

A one-page summary of what PreFlight is, who it's for, and where it could go.

## Problem

Every year, the music industry loses hundreds of millions of dollars in
royalties that are never paid to the artists who earned them. The money sits
in "black box" suspense accounts held by streaming platforms and collecting
societies, and after a few years it is redistributed to the largest
rightsholders by market share.

The root cause is almost never fraud. It's **bad metadata**: missing codes,
typos in writer names, split percentages that don't add up. These small
errors break the payment chain between the stream and the owner.

## Market size (with sources)

- **U.S. Mechanical Licensing Collective:** $424M in unclaimed mechanical
  royalties reported in 2021 alone.
- **Ivors Academy (UK):** estimated £500M/year in UK streaming black box.
- **Notes.fm (industry startup):** identified over $10M in unclaimed
  royalties in a one-year beta, averaging $15,500 per artist.

The category is validated: **Music Reports acquired Blokur** in 2024, whose
matching engine is designed to detect exactly this kind of unclaimed money.

## Target users

Three main segments could benefit from PreFlight:

1. **Independent artists and small labels** — as a last check before sending
   a release to their distributor.
2. **Music distributors** (DistroKid, TuneCore, Believe, CD Baby) — as a
   validation layer in their ingestion pipeline.
3. **Collecting societies** (SIAE, ASCAP, PRS) — as a way to reduce the size
   of their unallocated royalty pool.

## Value proposition

Most existing tools try to **recover** the money after it has been lost,
which is slow and often fails. PreFlight does the opposite: it moves the fix
to the moment **before** the release, when correcting a code or a name still
costs nothing.

For each detected issue, the tool tells the user three things: what is
wrong, why it causes revenue loss, and how to fix it.

## MVP scope (what's built today)

- Web form to input a track's metadata (title, artist, ISRC, ISWC,
  publisher, writers with splits and IPI).
- Seven validation rules (format checks, missing fields, split integrity,
  code linkage).
- Risk Score from 0 to 100 with color-coded severity.
- Report with prioritized issues and fix suggestions.
- PDF export of the report.
- History of past analyses.

## Not in scope for the MVP

- Integration with real industry registries (SIAE, MLC, ASCAP) — those
  require licensed partnerships and are not free APIs.
- Fuzzy name matching (e.g., "Mario Rossi" vs "M. Rossi").
- Economic estimation of the money at risk per issue.
- User accounts and multi-tenant catalog management.

These are deliberate cuts, not oversights. See the ROADMAP.md for how they
could enter later phases.

## Success metrics (how a real version would be measured)

- **For distributors:** percentage reduction of tracks flagged as
  "unmatched" by DSPs downstream.
- **For collecting societies:** reduction in unallocated pool size.
- **For artists:** self-reported money recovered vs. baseline.

For this MVP the only meaningful metric is functional: the seven rules
correctly identify their target errors on a set of test cases (verified via
18 automated tests).

## Competitive landscape

| Tool | Approach | Difference from PreFlight |
|---|---|---|
| **Blokur** (Music Reports) | Post-release matching | Reactive, needs licensed data access |
| **Notes.fm** | Portfolio audit for artists | Post-release, artist-facing |
| **Sound Credit** | Metadata management platform | Broader scope, paid, complex |
| **Distributor QA teams** | Manual review | Slow, inconsistent, doesn't scale |

PreFlight positions itself as a **pre-release validation layer**, upstream
of everything else in this list.

## Why I built this

I'm exploring music-tech product ideas. I wanted to pick a real, quantified
problem and build the smallest possible thing that could point at it — not
to solve the whole problem, but to prove the direction is worth pursuing.
