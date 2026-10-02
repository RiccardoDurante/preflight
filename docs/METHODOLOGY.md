# PreFlight — Royalty Risk Estimation Methodology

This document explains the formula PreFlight uses to estimate potential
euro royalty loss per validation issue, every number it relies on, where
each number comes from, and its limitations. It exists so the estimate is
never a "black box" — anyone can check the math and the sources.

**Status:** introduced in Phase 3 (v1.2). All figures below were verified
through dedicated research on 2026-10-02; see Sources at the end.

---

## The formula

- **expected_streams**: how many streams the track is expected to get in
  its first year. The user enters this on the form (it cannot be known
  automatically for an unreleased track). Default suggested value: 10,000
  streams, a illustrative placeholder for an emerging/independent artist,
  not a market statistic. The user should replace it with a real estimate
  when they have one (e.g. from a release plan or a label's projection).
- **per_stream_rate(territory)**: average euro value of one stream,
  looked up by the track's main market (USA, Italy, or Other). See table
  below.
- **at_risk_share(severity)**: the share of royalties estimated to be at
  risk for an issue of this severity. See table below.

This mirrors the original roadmap formula
(`estimated_streams x per-stream-rate x uncollected-share x territory-factor`),
simplified: instead of a separate "territory factor" multiplier applied to
one baseline rate, each territory has its own directly-sourced rate,
because the research found no single reliable baseline rate to multiply
from (see D17 in DECISION_LOG.md).

---

## Per-stream rate, by territory

| Territory | Rate (EUR) | Source | Strength |
|---|---|---|---|
| Italy | €0.0044 | FIMI 2025 report: paid-subscription streaming revenue (EUR 234.4M) divided by paid-subscription stream volume (54% of 99bn total streams = ~53.46bn), as reported by Music Business Worldwide citing FIMI/IFPI, published 2026-03-19. | Strong — official industry federation data, paid-only (clean comparison). |
| USA | €0.0037 (from $0.004) | RouteNote (routenote.com, updated 2025-05-22): Spotify $0.003-$0.005/stream. Chartlex (chartlex.com, published 2026-04-20, updated 2026-04-27): US $0.0039/stream. $0.004 is the point estimate where both agree. Converted to EUR at an assumed rate of 1 USD = EUR 0.92 (approximate, not live-updated). | Medium — two independent industry sources agree closely, but neither is an official platform disclosure, and the US figure (unlike Italy's) could not be cleanly isolated to paid-subscription-only streams from official data (RIAA does not publish stream counts). |
| Other / not specified | €0.0041 | Simple average of the Italy and USA rates above. | Weak — not derived from any market-specific data. Used only as a declared placeholder when the track's main market isn't USA or Italy. |

**Why Italy and USA specifically:** this project is Italian in origin, and
the USA is the single largest music market and the home of the MLC, the
richest public data source found for the "at-risk share" figures below.

**Why per-stream rates differ between markets despite similar subscription
prices:** Spotify's own Loud & Clear FAQ confirms royalties are pooled and
divided per market ("local pro-rata"): each country's subscription and ad
revenue funds a pool that is divided only among that country's own
streams. A market with more streams per subscriber (higher listening
intensity) mechanically has a lower per-stream rate, even at an identical
subscription price. Source: loudandclear.byspotify.com/faq/ (accessed
2026-10-02).

---

## At-risk share, by severity

| Severity | Share | Source |
|---|---|---|
| Red | 19.4% | The MLC (Mechanical Licensing Collective) 2024 Annual Report (official, as of 2025-03): $76,729,381 unclaimed + $110,270,109 unmatched = $187.0M, out of $969,527,027.57 collected for 2024 usage. (76,729,381 + 110,270,109) / 969,527,027.57 = 19.39%. |
| Amber | 7.1% | SCF (Italian connected-rights collecting society) FY2022 transparency report (official): EUR 2,892,088 explicitly labeled "non ripartibili per mancanza delle necessarie informazioni" (unmatchable for lack of necessary information), out of EUR 40.8M collected. |
| Info | 0% (no estimate) | "Info" issues (e.g. "could not check MusicBrainz right now") are not a metadata problem, so they carry no risk estimate. |

**Why red uses a US figure and amber uses an Italian figure:** no source
anywhere (MLC, CISAC, SIAE, academic literature) breaks unclaimed
royalties down by specific technical cause (missing ISRC vs missing ISWC
vs wrong name vs wrong split). These two figures are the best available
anchors, chosen to match PreFlight's own existing severity logic
(DECISION_LOG D7: red issues can block payment entirely, amber issues
only make payment uncertain) — not because they were measured for exactly
that distinction. The MLC's combined unclaimed+unmatched rate (19.4%, a
broad, current, large-market figure) is used for the more severe case;
SCF's narrower "missing information" rate (7.1%, which is conceptually
closer to "a specific metadata field is missing") is used for the less
severe case.

---

## Worked example

A track with 10,000 expected streams in Italy, with one red issue
("Writer splits sum to 90%, not 100%") and one amber issue ("Publisher
not specified"):

- Red issue: 10,000 x €0.0044 x 19.4% = **€8.54**
- Amber issue: 10,000 x €0.0044 x 7.1% = **€3.12**
- Aggregate estimate shown at the top of the report: **€11.66**

---

## Limitations (read before trusting this number)

1. **This is a heuristic, not a market-derived statistic.** No public
   source quantifies the royalty impact of a specific metadata error.
   The at-risk share percentages are anchors borrowed from broader,
   related figures (overall unclaimed royalty rates), not measurements of
   PreFlight's own validation rules.
2. **`expected_streams` is a guess, usually the user's.** The default
   (10,000) is an illustrative placeholder, not a prediction for any
   specific track.
3. **The USA rate is less solid than the Italy rate.** Italy's rate comes
   from an official federation's paid-only streaming revenue and volume.
   The USA rate comes from two industry blogs that happen to agree
   closely, cross-checked but not confirmed by an official paid-only
   stream count.
4. **The "Other" rate is not sourced to any market.** It's a plain average
   of the only two rates available, used only so the formula always
   returns a number.
5. **The formula assumes the whole issue amount is at risk, every year,
   for one year only.** It does not model partial recovery over time, or
   compounding across multiple release years.

This estimate is meant to communicate *relative* risk between issues (a
red issue is worth more than an amber one) and give an order of
magnitude — not to be read as a financial forecast.

---

## Sources

- The MLC, 2024 Annual Report: https://www.themlc.com/hubfs/The%20MLC%202024%20Annual%20Report.pdf
- SCF (Italy), FY2022 transparency report (cited in Phase 3 research notes)
- FIMI / Music Business Worldwide, 2025 Italian market report: https://www.musicbusinessworldwide.com/recorded-music-revenues-in-italy-grew-10-7-yoy-last-year-paid-streaming-revenues-in-the-market-jumped-14-1-yoy/
- RouteNote, streaming payout rates: https://routenote.com/blog/how-much-music-streaming-services-pay/
- Chartlex, Spotify royalty rates by country: https://www.chartlex.com/blog/money/spotify-royalty-rates-by-country-2026
- Spotify Loud & Clear FAQ: https://loudandclear.byspotify.com/faq/
- SIAE, FY2024 Transparency Report (checked, not used directly — see DECISION_LOG D17 for why SCF was preferred for the amber figure)
- CISAC Global Collections Report 2025 (checked — confirmed it does not break down unmatched royalties by cause)

Full research notes with additional detail and every source checked are
in this project's working history; the figures above are the ones that
made it into the formula.
