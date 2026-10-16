"""
Do critics predict Pixar's box office, and how much is a sequel worth?

Reads the CC0 pixarfilms data in data/, writes:
    reports/findings.json   numbers used by the dashboard
    reports/REPORT.md       the written analysis

Run:  python scripts/analysis.py
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REPORTS = ROOT / "reports"

# Released straight to Disney+ (Soul, Luca, Turning Red) or pulled from cinemas
# after one week by COVID-19 (Onward). Their box office isn't comparable.
NOT_COMPARABLE = {
    "Onward": "theatrical run cut short by COVID-19",
    "Soul": "released on Disney+",
    "Luca": "released on Disney+",
    "Turning Red": "released on Disney+",
}
SCORES = {
    "metacritic_score": "Metacritic",
    "rotten_tomatoes_score": "Rotten Tomatoes",
    "imdb_score": "IMDb",
    "letterboxd_rating": "Letterboxd",
}


def load() -> pd.DataFrame:
    films = pd.read_csv(DATA / "pixar_films.csv", parse_dates=["release_date"])
    df = (
        films
        .merge(pd.read_csv(DATA / "box_office.csv"), on="film", how="left")
        .merge(pd.read_csv(DATA / "public_response.csv"), on="film", how="left")
        .merge(pd.read_csv(DATA / "pixar_franchises.csv"), on="film", how="left")
    )
    first = df.groupby("franchise")["release_date"].transform("min")
    # A "follow-up" is any franchise film after the first: sequels and spin-offs (Lightyear).
    df["is_followup"] = df["franchise"].notna() & (df["release_date"] > first)
    df["year"] = df["release_date"].dt.year
    df["worldwide_m"] = df["box_office_worldwide"] / 1e6
    df["roi"] = df["box_office_worldwide"] / df["budget"]
    df["comparable"] = ~df["film"].isin(NOT_COMPARABLE)

    academy = pd.read_csv(DATA / "academy.csv")
    winners = set(academy.query("award_type == 'Animated Feature' and status == 'Won'")["film"])
    df["won_animated_feature"] = df["film"].isin(winners)
    df["animated_feature_eligible"] = df["year"] >= 2001  # category introduced for 2001 films
    return df


def bootstrap_spearman(x, y, n=5000, seed=0):
    rng = np.random.default_rng(seed)
    x, y = np.asarray(x), np.asarray(y)
    rhos = []
    for _ in range(n):
        i = rng.integers(0, len(x), len(x))
        rhos.append(stats.spearmanr(x[i], y[i]).statistic)
    return [float(np.percentile(rhos, 2.5)), float(np.percentile(rhos, 97.5))]


def main() -> None:
    REPORTS.mkdir(exist_ok=True)
    df = load()
    t = df[df["comparable"]].copy()

    # 1. Do critic and audience scores track box office?
    corr = []
    for col, label in SCORES.items():
        sub = t.dropna(subset=[col])
        for target, tlabel in (("worldwide_m", "Worldwide gross"), ("roi", "Return on budget")):
            res = stats.spearmanr(sub[col], sub[target])
            corr.append({
                "score": label, "target": tlabel, "rho": round(float(res.statistic), 2),
                "p": round(float(res.pvalue), 3),
                "ci": [round(v, 2) for v in bootstrap_spearman(sub[col], sub[target])],
            })

    # 2. Sequels vs originals
    groups = {}
    for key, g in (("originals", t[~t["is_followup"]]), ("followups", t[t["is_followup"]])):
        groups[key] = {
            "n": int(len(g)),
            "median_worldwide_m": round(float(g["worldwide_m"].median()), 1),
            "median_metacritic": float(g["metacritic_score"].median()),
            "median_roi": round(float(g["roi"].median()), 2),
        }
    mw_gross = stats.mannwhitneyu(t[t.is_followup]["worldwide_m"], t[~t.is_followup]["worldwide_m"])
    mw_score = stats.mannwhitneyu(t[t.is_followup]["metacritic_score"], t[~t.is_followup]["metacritic_score"])

    # 3. Regression: log gross ~ critics + follow-up + year
    t["log_gross"] = np.log(t["worldwide_m"])
    model = smf.ols("log_gross ~ metacritic_score + is_followup + year", data=t).fit()
    per10 = float(np.exp(model.params["metacritic_score"] * 10) - 1)
    per10_ci = [float(np.exp(v * 10) - 1) for v in model.conf_int().loc["metacritic_score"]]
    seq = float(np.exp(model.params["is_followup[T.True]"]) - 1)
    seq_ci = [float(np.exp(v) - 1) for v in model.conf_int().loc["is_followup[T.True]"]]

    # 4. Originals before vs after 2016
    t["era"] = np.where(t["year"] < 2016, "1995–2015", "2016–2026")
    era = (
        t.groupby(["era", "is_followup"])
        .agg(n=("film", "size"), median_worldwide_m=("worldwide_m", "median"),
             median_metacritic=("metacritic_score", "median"))
        .reset_index()
    )

    # 5. Oscars
    elig = df[df["animated_feature_eligible"]]
    oscar = {
        "winners": int(elig["won_animated_feature"].sum()),
        "eligible": int(len(elig)),
        "median_metacritic_winners": float(elig[elig.won_animated_feature]["metacritic_score"].median()),
        "median_metacritic_others": float(elig[~elig.won_animated_feature]["metacritic_score"].median()),
    }

    films = df[[
        "number", "film", "year", "budget", "box_office_worldwide", "worldwide_m", "roi",
        "metacritic_score", "rotten_tomatoes_score", "imdb_score", "cinema_score",
        "is_followup", "comparable", "won_animated_feature",
    ]].copy()
    films["note"] = films["film"].map(NOT_COMPARABLE).fillna("")
    films = films.replace({np.nan: None})
    findings = {
        "n_films": int(len(df)), "n_comparable": int(len(t)),
        "correlations": corr, "groups": groups,
        "mannwhitney_gross_p": round(float(mw_gross.pvalue), 3),
        "mannwhitney_metacritic_p": round(float(mw_score.pvalue), 3),
        "regression": {
            "n": int(model.nobs), "r2": round(float(model.rsquared), 2),
            "per_10_metacritic_pct": round(per10 * 100), "per_10_ci_pct": [round(v * 100) for v in per10_ci],
            "followup_pct": round(seq * 100), "followup_ci_pct": [round(v * 100) for v in seq_ci],
        },
        "era": era.to_dict(orient="records"),
        "oscar": oscar,
        "films": films.to_dict(orient="records"),
    }
    (REPORTS / "findings.json").write_text(json.dumps(findings, indent=2, default=str))

    def c(score, target):
        r = next(x for x in corr if x["score"] == score and x["target"] == target)
        return f"ρ = {r['rho']:.2f} (95% CI {r['ci'][0]:.2f} to {r['ci'][1]:.2f})"

    o, f = groups["originals"], groups["followups"]
    era_rows = "\n".join(
        f"| {r['era']} | {'Sequel / spin-off' if r['is_followup'] else 'Original'} | {r['n']} | "
        f"${r['median_worldwide_m']:,.0f}M | {r['median_metacritic']:.0f} |"
        for r in findings["era"]
    )
    reg = findings["regression"]
    report = f"""# Do critics predict Pixar's box office?

An analysis of all {len(df)} Pixar features, *Toy Story* (1995) through *Toy Story 5* (2026).
Box-office comparisons use the {len(t)} films with a normal theatrical release; *Onward*, *Soul*,
*Luca* and *Turning Red* are excluded (COVID-19 / Disney+ releases).

## Key findings

1. **Sequels earn about twice as much.** Median worldwide gross: **${f['median_worldwide_m']:,.0f}M** for
   sequels and spin-offs vs **${o['median_worldwide_m']:,.0f}M** for originals (Mann-Whitney p = {findings['mannwhitney_gross_p']}),
   even though sequels score a bit lower with critics (median Metacritic {f['median_metacritic']:.0f} vs {o['median_metacritic']:.0f}, p = {findings['mannwhitney_metacritic_p']}).
2. **Critics barely predict raw gross, but strongly predict return on budget.**
   Metacritic vs worldwide gross: {c('Metacritic', 'Worldwide gross')}. Metacritic vs return on budget:
   {c('Metacritic', 'Return on budget')}.
3. **Once you account for sequels, quality pays.** Controlling for sequel status and release year, every
   **+10 Metacritic points ≈ +{reg['per_10_metacritic_pct']}% worldwide gross**
   (95% CI +{reg['per_10_ci_pct'][0]}% to +{reg['per_10_ci_pct'][1]}%). Being a sequel adds about
   **+{reg['followup_pct']}%** (95% CI +{reg['followup_ci_pct'][0]}% to +{reg['followup_ci_pct'][1]}%). R² = {reg['r2']}, n = {reg['n']}.
4. **Originals have slipped since 2016.** Fewer originals, lower scores, lower grosses:

| Era | Type | Films | Median worldwide | Median Metacritic |
|---|---|---|---|---|
{era_rows}

5. **Oscar winners are the critics' darlings.** {oscar['winners']} of {oscar['eligible']} eligible films won Best Animated
   Feature; their median Metacritic is {oscar['median_metacritic_winners']:.0f} vs {oscar['median_metacritic_others']:.0f} for the rest.

## Why it matters

Raw gross is driven mostly by franchise recognition, which hides the effect of quality. Look at return
on budget, or control for sequel status, and critic scores matter a lot. For a studio, that means
originals need to be *great* to compete, and a well-reviewed sequel is close to a sure bet.

## Caveats

- **Small sample** ({len(t)} films). Correlations come with wide confidence intervals; treat the
  regression as descriptive, not causal.
- **Reverse causality is possible:** big franchise films may get more generous reviews.
- **Box office is not inflation-adjusted.** *Release year* in the regression absorbs some of this.
- **2026 grosses** (*Hoppers*, *Toy Story 5*) are a snapshot and may still be rising.

Data: [pixarfilms](https://github.com/erictleung/pixarfilms) (CC0). Not affiliated with Pixar or Disney.
"""
    (REPORTS / "REPORT.md").write_text(report, encoding="utf-8")
    print(f"Sequels median ${f['median_worldwide_m']:,.0f}M vs originals ${o['median_worldwide_m']:,.0f}M")
    print(f"+10 Metacritic ≈ +{reg['per_10_metacritic_pct']}% gross; sequel ≈ +{reg['followup_pct']}%")


if __name__ == "__main__":
    main()
