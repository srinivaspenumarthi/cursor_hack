# Paid to Hold the Bag: the Short-Term Reversal Premium Is a High-VIX Premium

Gator Quant Hacks 2026 · Track 03 Systematic Trading · quant note + reproducible code.

**Question.** Short-term reversal (buy last month's losers, sell last month's winners) is
the return to providing liquidity. If so, the premium should be largest when the
capital of liquidity providers is scarce, i.e. when VIX is high. We pre-registered that
hypothesis ([`HYPOTHESIS.md`](HYPOTHESIS.md), committed before any backtest), tested it on
36 years of daily data, and evaluated a two-year held-out period once.

**Answer, in one paragraph.** The state-dependence is real and replicates out of sample:
reversal returns rise with yesterday's VIX (Newey–West t ≈ 2.4 in-sample, 2.5–3.1
out-of-sample), and since 2004 the large-cap premium exists *only* in the top VIX quintile
(≈ 14 bps/day when VIX > 24, ≈ 0 otherwise; 52 bps/day on the 44 such days out of
sample). But it is an insurance premium: the book's volatility rises 3.6× with VIX, the
pay-off is concentrated in a handful of episodes, and the biggest losses (March 2020)
arrive inside the "good" state. Our pre-registered VIX-linear sizing rule therefore did
**not** beat constant exposure on Sharpe in-sample, vol-targeting *destroys* the strategy,
and a mean-variance rule we designed after the fact had a −53 % month. The tradeable
conclusion is a constant-notional (not constant-risk) large-cap book, sized for the
high-VIX drawdowns, run only by a desk with sub-10 bps all-in costs, with capacity of
roughly $100M–$500M for a market taker. The full argument is in the note.

## Reproduce everything (one command)

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run_all.py --oos                                 # downloads data, runs IS + OOS, writes results/
```

Takes ~30 s after the download. Outputs:

| Path | What |
|---|---|
| `results/REPORT.md` | every table in the note, auto-generated |
| `results/in_sample.json`, `results/out_of_sample.json` | all statistics, machine-readable |
| `results/figures/*.png` | every figure in the note |
| `results/tables/*.csv` | quintile tables, 36-variant sensitivity grid, cost curve, capacity |

Other commands:

```bash
python run_all.py                 # in-sample only (what we ran while developing; OOS stays locked)
python -m pytest -q               # 10 tests: no lookahead, cost accounting, metrics, OOS split rule
cd src && python -m gqh.capacity  # capacity table (square-root impact model)
python note/build_pdf.py          # rebuild note/quant_note.pdf from note/quant_note.md
```

No API keys. Data is downloaded from public sources at run time (see below) and cached in
`data/raw/` (git-ignored, per the track rule on not committing raw data).

## Data (all public, all cited in the note)

| Series | Source |
|---|---|
| Daily Short-Term Reversal factor `ST_Rev`; daily 6 portfolios formed on size and prior (−20,−1) return; Fama–French 5 factors; momentum factor | [Kenneth R. French Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html) (CRSP-based, updated through 2026-08) |
| CBOE VIX close (`VIXCLS`) | [FRED, Federal Reserve Bank of St. Louis](https://fred.stlouisfed.org/series/VIXCLS) |

Sample 1990-01-02 → 2026-08-31. In-sample to 2024-08-31; **out-of-sample 2024-09-01 →
2026-08-31** (the track's "most recent 20 % or 2 years, whichever is shorter" rule: the 2-year
cap binds).

## Repository layout

```
HYPOTHESIS.md            pre-registered hypothesis, rule, cost model, kill criteria (first commit)
run_all.py               reproduces the note: python run_all.py --oos
requirements.txt
data/download.py         downloads + parses French and FRED data (cached, git-ignored)
src/gqh/
  config.py              fixed constants: sample split, headline rule, cost model, variant grid
  data.py                loaders; lag_asof() aligns VIX strictly before each return day
  signals.py             constant / linear (headline) / regime rules; post-hoc vol-target and mean-variance
  backtest.py            P&L engine: weights × returns − costs on every dollar traded; break-even cost
  metrics.py             Sharpe, drawdown, turnover, Newey–West regressions, factor alpha, deflated Sharpe
  study.py               the study: in-sample, sensitivity grid, sub-periods, post-hoc, single OOS run
  capacity.py            square-root-impact capacity model
  plots.py, report.py    figures and results/REPORT.md
tests/                   pytest: no lookahead, cost accounting, scale invariance, split rule
note/                    quant_note.md → quant_note.pdf (build_pdf.py)
results/                 committed outputs so judges can compare against the note
```

## Honesty log

* `HYPOTHESIS.md` was committed at 2026-10-03 10:54 UTC, before the data pipeline existed.
* The in-sample study was committed at 11:11 UTC with the held-out period locked. The OOS
  flag was then run **once** (11:11:53 UTC; the report was re-rendered at 11:12:36 after a
  formatting-only change to `report.py`, with identical numbers) and committed separately.
* 38 strategy variants were evaluated in total: the 36 pre-registered in `HYPOTHESIS.md`
  plus 2 risk-aware rules designed after seeing the in-sample result. Both post-hoc rules are
  labelled as such everywhere and included in the deflated-Sharpe trial count.
* One bug was fixed after the first in-sample run: factor betas were reported in mixed units
  (returns in bps, factors in decimals). Alphas and t-stats were unaffected.
* Turnover of the French reversal portfolios is not observable from the public data; the 14 %
  one-way daily figure is derived in `HYPOTHESIS.md` and stress-tested (costs ×2, break-even cost).

## Team

Gator Quant Hacks 2026 · Systematic Trading Track. Contact via Devpost submission.
