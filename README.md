# Do critics predict Pixar's box office?

[![Reproducible](https://github.com/jsalerno12345/pixar-box-office-analysis/actions/workflows/reproduce.yml/badge.svg)](https://github.com/jsalerno12345/pixar-box-office-analysis/actions/workflows/reproduce.yml)

**[Interactive dashboard](https://jsalerno12345.github.io/pixar-box-office-analysis/)** · **[Full report](reports/REPORT.md)**

A short data science study of all 31 Pixar features, *Toy Story* (1995) through *Toy Story 5* (2026): how much do critic scores, sequels and awards relate to what a film earns?

## Findings

- **Sequels earn about twice as much.** Median worldwide gross is **$1.03B** for sequels and spin-offs vs **$525M** for originals, even though sequels score a bit lower with critics.
- **Critics barely predict raw gross, but strongly predict return on budget** (Metacritic: ρ = 0.35 vs gross, ρ = 0.65 vs return on budget).
- **Once sequels are accounted for, quality pays.** Holding sequel status and release year fixed, **+10 Metacritic points ≈ +32% worldwide gross** (95% CI +12% to +55%).
- **Originals have slipped since 2016:** median Metacritic 89 → 70 and median gross $534M → $443M for theatrical originals.
- **Oscar winners are the critics' favorites:** median Metacritic 90 for Best Animated Feature winners vs 71 for the rest.

## Method

- **Fair comparison set.** *Onward* (theatrical run cut short by COVID-19) and *Soul*, *Luca* and *Turning Red* (released on Disney+) are excluded from box-office comparisons, leaving 27 films.
- **Rank correlations** (Spearman) with bootstrap confidence intervals, because box office is heavily skewed and n is small.
- **Log-linear regression** of worldwide gross on Metacritic, sequel status and release year, reported as percentage effects.
- **Sequel** means any franchise film after the first, including the spin-off *Lightyear*.

## Caveats

Small sample, descriptive rather than causal, nominal (not inflation-adjusted) dollars, and 2026 grosses are a snapshot. Big franchise films may also get kinder reviews, so the arrow could point both ways. Details in the [report](reports/REPORT.md).

## Run it

```bash
pip install -r requirements.txt
python scripts/analysis.py         # → reports/findings.json, reports/REPORT.md
python scripts/build_dashboard.py  # → index.html
```

GitHub Actions re-runs the analysis on every push and fails if the committed results don't reproduce.

## Data

[`pixarfilms`](https://github.com/erictleung/pixarfilms) by Eric Leung, CC0 1.0, snapshot August 2026 (see [`data/SOURCE.md`](data/SOURCE.md)).
This project is not affiliated with or endorsed by Pixar or Disney.
