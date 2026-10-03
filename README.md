# Paid to Hold the Bag: Liquidity Provision Is a High-VIX Premium

Gator Quant Hacks 2026 · Track 03 Systematic Trading · quant note + reproducible code.

**Question.** Short-term reversal — being the counterparty to someone who must trade now —
is the return to providing liquidity. If so, the premium should be largest when the capital
of liquidity providers is scarce, i.e. when VIX is high. We pre-registered that hypothesis
and tested the *one* mechanism on two independent instruments, each with its own
hypothesis file committed before its first backtest, and each with a two-year held-out
period evaluated once:

* **Module A** ([`HYPOTHESIS.md`](HYPOTHESIS.md)): daily short-term reversal portfolios from
  Kenneth French, 1990–2026, with a pre-registered rule that *levers* exposure by lagged VIX.
* **Module B** ([`HYPOTHESIS_B.md`](HYPOTHESIS_B.md)): fading overnight gaps in S&P 500 names
  from the opening to the closing auction, 2005–2026, with a pre-registered rule that
  *participates* only when lagged VIX ≥ 20 — the lesson of Module A applied.

**Answer, in one paragraph.** The state-dependence is real and replicates out of sample in
both modules. A: reversal returns rise with yesterday's VIX (Newey–West t ≈ 2.4 in-sample,
2.5–3.1 out-of-sample); since 2004 the large-cap premium exists *only* in the top VIX
quintile (≈ 14 bps/day when VIX > 24, ≈ 0 otherwise; 52 bps/day on the 44 such days out of
sample). But the book's volatility rises 3.6× with VIX, so the VIX-levered rule did **not**
beat constant exposure on Sharpe, vol-targeting *destroys* the strategy, and a post-hoc
mean-variance rule had a −53 % month. B: the gap fade earns 18 bps/day gross (t = 12, gross
Sharpe 3.3), 35 bps/day in the top VIX quintile vs 12 elsewhere, both legs contributing; at
5 bps per dollar traded it is a market maker's premium (always-on nets nothing), and the
participation rule lifts net Sharpe from −0.26 to +0.12 in-sample and from −1.83 to +0.24
out of sample, where the top-VIX state paid 56 bps/day and every other state zero. The
premium has decayed (33 bps/day before 2013, 8 after). Tradeable conclusion: a
constant-notional large-cap reversal book (net Sharpe ≈ 0.4, break-even 14 bps, $100M–$500M
capacity) and, for a desk with ~2.5 bps auction execution, a VIX-gated gap fade (Sharpe ≈ 1,
tens of millions of capacity). Full argument in [`note/quant_note.pdf`](note/quant_note.pdf).

## Reproduce everything (one command)

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run_all.py --oos                                 # downloads data, runs IS + OOS for both modules, writes results/
```

Takes ~1 minute after the downloads (French/FRED files and ~500 tickers of daily
open/close via `yfinance`). Outputs:

| Path | What |
|---|---|
| `results/REPORT.md`, `results/REPORT_B.md` | every table in the note, auto-generated (Module A / Module B) |
| `results/in_sample.json`, `results/out_of_sample.json` | Module A statistics, machine-readable |
| `results/gapfade_in_sample.json`, `results/gapfade_out_of_sample.json` | Module B statistics |
| `results/figures/*.png` | every figure in the note |
| `results/tables/*.csv` | quintile tables, sensitivity grids (36 + 24 variants), cost curve, capacity, daily P&L |

Other commands:

```bash
python run_all.py                 # in-sample only (what we ran while developing; OOS stays locked)
python run_all.py --skip-module-b # Module A only (no yfinance needed)
python -m pytest -q               # 17 tests: no lookahead, point-in-time universe, cost accounting, split rule
cd src && python -m gqh.capacity  # Module A capacity table (square-root impact model)
python note/build_pdf.py          # rebuild note/quant_note.pdf from note/quant_note.md (needs Chrome/Chromium)
```

No API keys. Data is downloaded from public sources at run time and cached in `data/raw/`
and `data/processed/` (git-ignored, per the track rule on not committing raw data). The
only committed data file is `data/sp500_constituents.csv`, a 503-row snapshot of the
Wikipedia constituent list that defines Module B's universe.

## Data (all public, all cited in the note)

| Series | Source |
|---|---|
| Daily Short-Term Reversal factor `ST_Rev`; daily 6 portfolios formed on size and prior (−20,−1) return; Fama–French 5 factors; momentum factor | [Kenneth R. French Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html) (CRSP-based, through 2026-08) |
| CBOE VIX close (`VIXCLS`) | [FRED, Federal Reserve Bank of St. Louis](https://fred.stlouisfed.org/series/VIXCLS) |
| Daily adjusted open/close, current S&P 500 constituents | Yahoo Finance via [`yfinance`](https://github.com/ranaroussi/yfinance); constituent list and index-addition dates from [Wikipedia](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies), snapshot 2026-10-03 |

Samples: A 1990-01-02 → 2026-08-31; B 2005-01-03 → 2026-08-31. In-sample to 2024-08-31 for
both; **out-of-sample 2024-09-01 → 2026-08-31** (the track's "most recent 20 % or 2 years,
whichever is shorter" rule: the 2-year cap binds). Module B's universe is point-in-time on
the way in (a stock enters only from its index-addition date) but survivorship-biased on the
way out (removed names are missing); the note discloses this and tests it (both legs of the
spread contribute symmetrically). Yahoo may revise prices after the fact; the cached download
is what the committed results were produced from.

## Repository layout

```
HYPOTHESIS.md            Module A: pre-registered hypothesis, rule, cost model, kill criteria (first commit)
HYPOTHESIS_B.md          Module B: pre-registered hypothesis, universe, rule, cost model, kill criteria
run_all.py               reproduces the note: python run_all.py --oos
requirements.txt
data/download.py         French + FRED (cached, git-ignored)
data/download_stocks.py  yfinance open/close for the constituent list (cached, git-ignored)
data/snapshot_constituents.py, data/sp500_constituents.csv   frozen universe for Module B
src/gqh/
  config.py              fixed constants: sample split, Module A headline rule, cost model, variant grid
  data.py                loaders; lag_asof() aligns VIX strictly before each return day
  signals.py             constant / linear (headline) / regime rules; post-hoc vol-target and mean-variance
  backtest.py            Module A P&L engine: weights × returns − costs on every dollar traded; break-even cost
  metrics.py             Sharpe, drawdown, Newey–West regressions, factor alpha, deflated Sharpe
  study.py               Module A study: in-sample, grid, sub-periods, post-hoc, single OOS run
  gapfade.py             Module B: panel construction, participation rule, backtest, tests, grid, figures, single OOS run
  capacity.py            square-root-impact capacity model
  plots.py, report.py, report_b.py    figures and results/REPORT*.md
tests/                   pytest: no lookahead, point-in-time membership, cost accounting, split rule
note/                    quant_note.md → quant_note.pdf (build_pdf.py)
results/                 committed outputs so judges can compare against the note
```

## Honesty log

* Module A: `HYPOTHESIS.md` committed 2026-10-03 10:54 UTC, before the data pipeline existed.
  In-sample study committed 11:11 UTC with the held-out period locked; `--oos` run **once** and
  committed separately at 11:12 UTC.
* Module B: `HYPOTHESIS_B.md` and the frozen constituent list committed 11:53:57 UTC, before
  any single-stock price was downloaded. In-sample committed 12:01:40; `--oos` run **once** and
  committed 12:02:08.
* 62 strategy variants in total: 36 pre-registered in `HYPOTHESIS.md`, 2 post-hoc risk-aware
  rules for Module A (labelled as such everywhere, included in the deflated-Sharpe trial count),
  24 pre-registered in `HYPOTHESIS_B.md`. The Module B sub-period split (2005–2012 / 2013–2024)
  was chosen after seeing the by-year table and is labelled descriptive.
* One bug was fixed after Module A's first in-sample run: factor betas were reported in mixed
  units. Alphas and t-stats were unaffected. One data-cleaning rule in Module B (|gap| > 20 %
  excluded, using open-time information only) was not in the hypothesis file; results without
  it are reported and differ by 0.1 bps.
* Turnover of the French reversal portfolios is not observable from public data; the 14 %
  one-way daily figure is derived in `HYPOTHESIS.md` and stress-tested. Module B's execution
  at the official open is an assumption; its cost is stressed from 2.5 to 10 bps.
* We were given a practitioner's intraday gap-trading strategy matrix and ML-ops code. It
  contained no price or trade data and was used only to motivate Module B's design.

## Team

Gator Quant Hacks 2026 · Systematic Trading Track. Contact via Devpost submission.
