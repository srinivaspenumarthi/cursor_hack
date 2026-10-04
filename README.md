# Paid to Hold the Bag: Liquidity Provision Is a High-VIX Premium

Gator Quant Hacks 2026 · Track 03 Systematic Trading + Massive · one repository.

**Public repository:** https://github.com/srinivaspenumarthi/cursor_hack

This is the only repo to submit. It holds two finished studies. Their numbers are not averaged and neither 2026 window was rerun to produce this copy.

| Track | Where | Graded result |
|---|---|---|
| Systematic trading | this directory | [`note/quant_note.pdf`](note/quant_note.pdf). Liquidity premium rises with lagged VIX. Net Sharpe about 0.4 constant; gated gap fade +0.12 in-sample and +0.24 held out. `python run_all.py --oos` |
| Massive 8-K | [`filing_edge/`](filing_edge/) | [`filing_edge/submission/Massive_Research_Note.pdf`](filing_edge/submission/Massive_Research_Note.pdf) (2 pages) and [`filing_edge/submission/Systematic_Trading_Note.pdf`](filing_edge/submission/Systematic_Trading_Note.pdf) (5 pages). Cash-secured puts after buyback filings, NBBO quotes, funded account. Development −186 bps. Held-out account lost $796 on $1 million. Decision: do not trade. |

The daily-bar 8-K study in this directory (`HYPOTHESIS_8K.md`, appendix A6) is an earlier failed test on last-trade closes. Filing Edge is the Massive study. Both failures stay in the repo. The saved Massive replay is [srinivaspenumarthi.github.io/hack](https://srinivaspenumarthi.github.io/hack/), and the same pages are in `filing_edge/docs/`.

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
* **Module C** ([`HYPOTHESIS_C.md`](HYPOTHESIS_C.md)): an attempt to beat VIX with a sharper
  state variable — the variance risk premium (price of risk) separated from realised
  variance (quantity of risk), plus VIX term-structure backwardation — on the same books.
  **Rejected as pre-specified**, and reported in full.

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
premium has decayed (33 bps/day before 2013, 8 after). C: the premium loads on *realised*
variance, not on the variance risk premium; VRP rules lose to constant exposure in and out of
sample; backwardation helped one book in-sample and did not replicate — so no public state
variable we found selects the premium without selecting the volatility, which is the
strongest support for the constant-notional conclusion. Tradeable conclusion: a
constant-notional large-cap reversal book (net Sharpe ≈ 0.4, break-even 14 bps, $100M–$500M
capacity) and, for a desk with ~2.5 bps auction execution, a VIX-gated gap fade (Sharpe ≈ 1,
tens of millions of capacity). Full argument in [`note/quant_note.pdf`](note/quant_note.pdf).

## Reproduce everything (one command)

```bash
git clone https://github.com/srinivaspenumarthi/cursor_hack.git
cd cursor_hack
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run_all.py --oos                                 # downloads data, runs IS + OOS for both modules, writes results/
```

Takes ~1 minute after the downloads (French/FRED files and ~500 tickers of daily
open/close via `yfinance`). Outputs:

| Path | What |
|---|---|
| `results/REPORT.md`, `results/REPORT_B.md`, `results/REPORT_C.md` | every table in the note, auto-generated (Modules A / B / C) |
| `results/in_sample.json`, `results/out_of_sample.json` | Module A statistics, machine-readable |
| `results/gapfade_in_sample.json`, `results/gapfade_out_of_sample.json` | Module B statistics |
| `results/pricing_in_sample.json`, `results/pricing_out_of_sample.json` | Module C statistics |
| `results/figures/*.png` | every figure in the note |
| `results/tables/*.csv` | quintile tables, sensitivity grids (36 + 24 + 18 variants), cost curve, capacity, daily P&L |

Other commands:

```bash
python run_all.py                 # in-sample only (what we ran while developing; OOS stays locked)
python run_all.py --skip-module-b # Module A only (no yfinance needed)
python today.py                   # operational view: latest VIX, Module B gate, expected premium vs toll, Module A sizing
python -m pytest -q               # lookahead, point-in-time universe, costs, paper fills, and the 8-K entry clock
cd src && python -m gqh.capacity  # Module A capacity table (square-root impact model)
python note/build_pdf.py          # rebuild note/quant_note.pdf from note/quant_note.md (needs Chrome/Chromium)
```

The liquidity study above does not use API keys. A second, separate study — cash-secured
puts after repurchase 8-Ks — does. It is specified in `HYPOTHESIS_8K.md` and does not
recompute the liquidity out-of-sample window.

```bash
pip install -r requirements.txt          # adds dotenv, psycopg, databento, pypdf
cp .env.example .env                     # MASSIVE_API_KEY, DATABENTO_API_KEY, DATABASE_URL
python run_eightk.py --start 2023-01-01 --end 2025-12-31
python run_eightk.py --start 2026-01-01 --end 2026-08-31   # once, after the in-sample commit
```

The second command refuses to run if `results/eightk_out_of_sample.json` already exists,
and either command refuses a window that crosses 2026-01-01. Outputs:
`results/eightk_in_sample.json`, `results/eightk_horizons_is.csv`, `results/eightk_variant_grid.csv`
(54 variants, in-sample only), `results/figures/eightk_equity_is.png`, and the same names with
`_oos` after the single out-of-sample run. Gemini writes `results/eightk_briefing.txt` from
those numbers. ElevenLabs writes an mp3 only when `ELEVENLABS_API_KEY` is set.

What that study found, and why it is not the submission's claim: in-sample, 300 repurchase
8-Ks in the 2022 top-100, 18 pairs still quoted 21 sessions later, event minus control
**−120 bps** (95% interval −293 to +52). The pre-registered test fails. Out of sample,
opened once after that commit, the 21-session difference is +1,043 bps on 3 pairs
(interval −3,816 to +5,902). The sign flips, which the hypothesis also treats as a failure.
The liquidity result in the note is unchanged. Appendix A6 of `note/quant_note.md` has the
full accounting. The first option pull used Massive for 3,234 contracts; Databento was asked
88 times when Massive had no bar and added none.

Raw bars and filings are cached in `data/raw/` and `data/processed/` (git-ignored; no API
keys and no licensed bars are committed). The only committed market file for the liquidity
study is `data/sp500_constituents.csv`, a 503-row snapshot of the Wikipedia constituent list.

## Data (all public, all cited in the note)

| Series | Source |
|---|---|
| Daily Short-Term Reversal factor `ST_Rev`; daily 6 portfolios formed on size and prior (−20,−1) return; Fama–French 5 factors; momentum factor | [Kenneth R. French Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html) (CRSP-based, through 2026-08) |
| CBOE VIX close (`VIXCLS`); CBOE 3-month VIX (`VXVCLS`, from 2007-12) | [FRED, Federal Reserve Bank of St. Louis](https://fred.stlouisfed.org/series/VIXCLS) |
| Daily adjusted open/close, current S&P 500 constituents | Yahoo Finance via [`yfinance`](https://github.com/ranaroussi/yfinance); constituent list and index-addition dates from [Wikipedia](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies), snapshot 2026-10-03 |
| 8-K study: 2022 dollar volume, stock bars, option daily bars | [Massive](https://massive.com) grouped daily and ticker aggregates. The filings endpoint ignores `cik` / `ticker` / `filing_date` filters, so it is not used for discovery |
| 8-K study: repurchase filings and acceptance timestamps | SEC full-text index (`efts.sec.gov`) and submissions JSON (`data.sec.gov`), public, no key |
| 8-K study: option bars Massive does not have | [Databento](https://databento.com) OPRA.PILLAR `ohlcv-1d`, one OCC contract per call, $2/call and $40 study cap. Parent `*.OPT` streams are not requested |
| 8-K study: filing and bar store | TigerData (Timescale) tables `eightk_filings`, `eightk_option_bars` when `DATABASE_URL` is set. Disk cache is the fallback |

Samples: A 1990-01-02 → 2026-08-31; B 2005-01-03 → 2026-08-31. In-sample to 2024-08-31 for
both; **out-of-sample 2024-09-01 → 2026-08-31** (the track's "most recent 20 % or 2 years,
whichever is shorter" rule: the 2-year cap binds). Module B's universe is point-in-time on
the way in (a stock enters only from its index-addition date) but survivorship-biased on the
way out (removed names are missing); the note discloses this and tests it (both legs of the
spread contribute symmetrically). Yahoo's adjusted prices differ by < 0.1 % between downloads
(adjustment-factor rounding), so a fresh run reproduces Module B to the precision quoted in
the note (e.g. 17.8 bps gross, Sharpe −0.26 / +0.12) but not bit-for-bit; we verified this
with a clean clone. The committed `results/tables/gapfade_panel_daily.csv` holds the derived
daily portfolio series (not raw prices) from which every Module B statistic can be
recomputed exactly.

## Live / paper-trading layer (`live/`)

The research answers "is the premium real and when does it pay?". `live/` is the operational
loop that would trade Module B's rule, built so that every production assumption the backtest
makes can be *measured* rather than assumed. It is paper-trading by default (simulated
auction fills, pre-registered cost toll) and never imports from `src/gqh` except for the
pre-registered constants, so research and operations cannot drift apart silently.

```bash
pip install -r requirements-live.txt
cp .env.example .env                    # add MASSIVE_API_KEY (required); the rest are optional
python -m live replay --date 2026-07-30 # run the full cycle on a past session with historical data
python -m live status --days 20         # operator dashboard, text
python -m live schedule                 # run the daily cycle on a clock (blocking; ET)
streamlit run live/dashboard.py --server.port 8765   # same dashboard in the browser
```

The browser dashboard has five tabs. **Today**: the gate, VIX_{t−1}, the VIX/VIX3M term ratio,
universe size, cumulative net P&L and the per-session table (gross, cost, net, the rule book's
spread whether or not we traded, basket overlap, implementation shortfall), today's step log,
risk events, and open positions marked to the last trade. **Session detail**: the target
baskets and every order. **Research**: the committed in-sample VIX-quintile table and every
figure from the note, which do not move when the paper book trades. **Replay**: run or reset a
past session and ask for the Gemini briefing. **8-K puts**: the separate repurchase-filing
study, in-sample and out-of-sample, read from the committed JSON. It does not change the
gap-fade book. The sidebar holds the kill switch. The page reads the store and never submits
an order of its own.

Daily cycle (all times ET, each step idempotent and audited in the store):

| Time | Step | What happens |
|---|---|---|
| 08:45 | `pre_open` | VIX_{t−1} from Massive → Yahoo → FRED (first that answers, with the date it refers to); gate ON iff ≥ 20; universe as of today (point-in-time constituents). |
| 09:27 | `open_auction` | Pre-open indicative prices: Nasdaq NOII reference price via Databento (the auction's own estimate, published every second from 09:25), else Massive pre-market last trade / fair value. Gaps → relgap quintiles → dollar-neutral targets → pre-trade risk checks → market-on-open orders before the 09:28 cut-off. |
| 09:35 | `post_open` | Official opening prints → fills; positions written to the store; book-vs-broker reconciliation; basket overlap vs the official-open book. |
| every 5 min | `monitor_intraday` | Mark positions at last trade; same-day disaster stop (default 5 % of gross, a >3σ day) flattens at market. |
| 15:45 | `close_auction` | Market-on-close orders for every open position (NYSE cut-off 15:50). |
| 16:20 | `eod` | Official closes → fills, P&L net of the toll, flatness check, reconciliation, implementation shortfall; the rule's book is also evaluated on days we did *not* trade so the premium is monitored while out. |

Components: `feeds/massive.py` (official daily OHLC — its open matches the Nasdaq auction
reference price to the cent — plus real-time snapshots and market status), `feeds/vix.py`,
`feeds/databento_feed.py` (cost-guarded: every query is priced before it runs; a day of NOII
for the universe costs about one cent), `store.py` (Timescale/Postgres hypertables if
`DATABASE_URL` is set, else SQLite — same schema), `signal.py`, `risk.py`, `broker/paper.py`
(fills at the official auction prints, charges c_base × VIX_{t−1}/20 bps per dollar),
`broker/alpaca.py` (native `opg`/`cls` auction orders; activates when Alpaca keys are present;
not exercised against a funded account here), `scheduler.py`, `monitor.py`, `briefing.py`
(optional Gemini summary of the dashboard; it summarises numbers, it decides nothing).

Risk controls: kill-switch file (`python -m live kill`), duplicate-session guard, VIX gate,
stale-VIX and stale-indicative blocks, universe-coverage floor (the pre-registered 100 names),
gross and per-name limits, one-sided/dollar-neutrality checks, same-day disaster stop,
overnight-position check, reconciliation. A trailing multi-day loss is deliberately a
*warning for human review*, not an automatic halt: the research shows that cutting exposure
after losses removes the premium (§5.2, §5.4 of the note).

What the replays showed (March–April 2026 volatility episode, gate ON on 11 sessions): the
baskets chosen on 09:27 indicative prices overlap the official-open baskets by 74–86 %,
i.e. one name in five changes quintile between the last indicative print and the auction —
a production fact the backtest cannot see, and the first thing to improve (later submission,
or an imbalance-aware estimate of the open). Implementation shortfall from this is recorded
per session in `live_pnl.shortfall_bps`. The wider set in appendix A7 of the note is 12
high-VIX sessions across 2026 (overlap 74–92 %, shortfall −47 to +29 bps/day). Same clock
check, larger sample. Neither sample replaces the headline backtest.

Keys live in `.env` (git-ignored; `.env.example` documents every variable). Without any key
the research pipeline is unaffected; without `MASSIVE_API_KEY` the live layer does not start.

## Repository layout

```
HYPOTHESIS.md            Module A: pre-registered hypothesis, rule, cost model, kill criteria (first commit)
HYPOTHESIS_B.md          Module B: pre-registered hypothesis, universe, rule, cost model, kill criteria
HYPOTHESIS_C.md          Module C: pre-registered decomposition (VRP vs realised variance), rules, kill criteria
HYPOTHESIS_8K.md         8-K puts: pre-registered before any filing or option bar was stored
run_all.py               reproduces the liquidity note: python run_all.py --oos
run_eightk.py            8-K study: python run_eightk.py --start YYYY-MM-DD --end YYYY-MM-DD
today.py                 daily state check from the cached data
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
  pricing.py             Module C: VRP / RV / term-structure states, double sorts, rule comparison on all books, single OOS run
  capacity.py            square-root-impact capacity model
  plots.py, report*.py   figures and results/REPORT*.md
  eightk_logic.py        8-K rules: entry clock, strike, expiry, haircut, paired test (no network)
  eightk_pull.py         Massive + SEC + Databento pulls, TigerData writes, disk cache
live/                    paper/live trading layer: feeds, signal, risk, broker, store, scheduler, monitor (python -m live)
tests/                   pytest: no lookahead, point-in-time membership, cost accounting, split rule; live-layer fills/risk/flatness
note/                    quant_note.md → quant_note.pdf (build_pdf.py)
requirements-live.txt    extra dependencies for live/ (dotenv, psycopg, apscheduler, databento)
.env.example             every credential and limit the live layer reads; copy to .env (git-ignored)
results/                 committed outputs so judges can compare against the note
```

## Honesty log

* Module A: `HYPOTHESIS.md` committed 2026-10-03 10:54 UTC, before the data pipeline existed.
  In-sample study committed 11:11 UTC with the held-out period locked; `--oos` run **once** and
  committed separately at 11:12 UTC.
* Module B: `HYPOTHESIS_B.md` and the frozen constituent list committed 11:53:57 UTC, before
  any single-stock price was downloaded. In-sample committed 12:01:40; `--oos` run **once** and
  committed 12:02:08.
* Module C: `HYPOTHESIS_C.md` committed 18:14:13 UTC, before any VRP or term-structure series
  was computed. In-sample committed 18:19:02; `--oos` run **once** and committed 18:19:38.
* 80 strategy variants in total: 36 pre-registered in `HYPOTHESIS.md`, 2 post-hoc risk-aware
  rules for Module A (labelled as such everywhere, included in the deflated-Sharpe trial count),
  24 pre-registered in `HYPOTHESIS_B.md`, 18 pre-registered in `HYPOTHESIS_C.md`. The Module B
  sub-period split (2005–2012 / 2013–2024) was chosen after seeing the by-year table and is
  labelled descriptive.
* One bug was fixed after Module A's first in-sample run: factor betas were reported in mixed
  units. Alphas and t-stats were unaffected. One data-cleaning rule in Module B (|gap| > 20 %
  excluded, using open-time information only) was not in the hypothesis file; results without
  it are reported and differ by 0.1 bps.
* Turnover of the French reversal portfolios is not observable from public data; the 14 %
  one-way daily figure is derived in `HYPOTHESIS.md` and stress-tested. Module B's execution
  at the official open is an assumption; its cost is stressed from 2.5 to 10 bps.
* We were given a practitioner's intraday gap-trading strategy matrix and ML-ops code. It
  contained no price or trade data and was used only to motivate Module B's design.
* Opening-price clock: a market-on-open fill at the official open is the auction print, not lookahead. Sorting the basket on that same open is. The names are chosen in the backtest with a price that does not exist until the auction. Twelve replayed 2026 sessions, inside the holdout, put the 09:27 indicative basket at 74–92% overlap with the official-open basket and the shortfall at −47 to +29 bps/day. The headline was not replaced with that sample. The gross Sharpe of 3.3 is before the toll; after 5 bps per side it is −0.26 always-on and +0.12 gated.
* Reused holdout: 2024-09-01 → 2026-08-31 was opened once for Module A at 11:12 UTC. Module B's hypothesis was written at 11:53, after that result, and Module C's at 18:14, after both. Each module's own numbers were computed once and not refit. The window was not untouched. A's out-of-sample slope is the clean confirmation. Appendix A7 of the note.
* 8-K study: `HYPOTHESIS_8K.md` committed 2026-10-04 00:54 UTC, before any filing or option
  bar was stored. In-sample committed 01:53 UTC (`80b867f`). A scoring bug that pooled all
  54 variants into the headline was fixed and recomputed from the cached bars *before* that
  commit; the discarded pass was never the recorded result. Out of sample was then run
  **once**, 01:55 UTC, and committed 01:57 UTC (`f66c2d9`). The program refuses a second pass.
  That study uses daily last trades. The Massive study with NBBO quotes is `filing_edge/`,
  copied in with its development and held-out reports already written. Copying it did not
  reprice either window.

## Team

Gator Quant Hacks 2026 · Systematic Trading Track. Contact via Devpost submission.
