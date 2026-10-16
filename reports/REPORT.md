# Do critics predict Pixar's box office?

An analysis of all 31 Pixar features, *Toy Story* (1995) through *Toy Story 5* (2026).
Box-office comparisons use the 27 films with a normal theatrical release; *Onward*, *Soul*,
*Luca* and *Turning Red* are excluded (COVID-19 / Disney+ releases).

## Key findings

1. **Sequels earn about twice as much.** Median worldwide gross: **$1,029M** for
   sequels and spin-offs vs **$525M** for originals (Mann-Whitney p = 0.041),
   even though sequels score a bit lower with critics (median Metacritic 73 vs 80, p = 0.145).
2. **Critics barely predict raw gross, but strongly predict return on budget.**
   Metacritic vs worldwide gross: ρ = 0.35 (95% CI 0.00 to 0.62). Metacritic vs return on budget:
   ρ = 0.65 (95% CI 0.31 to 0.84).
3. **Once you account for sequels, quality pays.** Controlling for sequel status and release year, every
   **+10 Metacritic points ≈ +32% worldwide gross**
   (95% CI +12% to +55%). Being a sequel adds about
   **+68%** (95% CI +16% to +142%). R² = 0.44, n = 27.
4. **Originals have slipped since 2016.** Fewer originals, lower scores, lower grosses:

| Era | Type | Films | Median worldwide | Median Metacritic |
|---|---|---|---|---|
| 1995–2015 | Original | 12 | $534M | 89 |
| 1995–2015 | Sequel / spin-off | 4 | $652M | 76 |
| 2016–2026 | Original | 4 | $443M | 70 |
| 2016–2026 | Sequel / spin-off | 7 | $1,066M | 73 |

5. **Oscar winners are the critics' darlings.** 11 of 28 eligible films won Best Animated
   Feature; their median Metacritic is 90 vs 71 for the rest.

## Why it matters

Raw gross is driven mostly by franchise recognition, which hides the effect of quality. Look at return
on budget, or control for sequel status, and critic scores matter a lot. For a studio, that means
originals need to be *great* to compete, and a well-reviewed sequel is close to a sure bet.

## Caveats

- **Small sample** (27 films). Correlations come with wide confidence intervals; treat the
  regression as descriptive, not causal.
- **Reverse causality is possible:** big franchise films may get more generous reviews.
- **Box office is not inflation-adjusted.** *Release year* in the regression absorbs some of this.
- **2026 grosses** (*Hoppers*, *Toy Story 5*) are a snapshot and may still be rising.

Data: [pixarfilms](https://github.com/erictleung/pixarfilms) (CC0). Not affiliated with Pixar or Disney.
