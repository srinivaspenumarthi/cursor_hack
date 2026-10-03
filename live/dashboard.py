"""Operator dashboard for the VIX-gated gap fade.

    streamlit run live/dashboard.py --server.port 8765 --server.address 0.0.0.0

Read-only over the store and the committed research artefacts, except three actions: the kill
switch, replaying a past session, and an optional Gemini briefing. Nothing here places an order.
"""
from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from live import clock, dashboard_data as data  # noqa: E402
from live.settings import SETTINGS  # noqa: E402

st.set_page_config(page_title="Gap Fade — paper book", layout="wide")

st.markdown("""
<style>
.block-container { padding-top: 1.4rem; }
div[data-testid="stMetric"] { background: #11161d; border: 1px solid #262e38; border-radius: 10px; padding: 10px 14px; }
div[data-testid="stMetric"] label { color: #9aa4b2; }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def store():
    from live.store import Store
    return Store()


@st.cache_resource
def feed():
    from live.feeds.massive import MassiveFeed
    return MassiveFeed()


@st.cache_data(ttl=300)
def research():
    return data.research_view()


def _bps(x, signed=True) -> str:
    if x is None or pd.isna(x):
        return "—"
    return f"{x:+.1f}" if signed else f"{x:.1f}"


# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown("**Gap fade · paper book**")
    session = st.date_input("Session", clock.session_date(), max_value=clock.session_date(), key="session_date")
    n_days = st.slider("History (sessions)", 5, 120, 40)
    auto = st.toggle("Auto-refresh every 30s", value=False)
    st.divider()
    view = data.live_view(store(), session, n_days)
    if view["kill_switch"]:
        st.error("Kill switch is ENGAGED. No orders will be sent.")
        if st.button("Release kill switch", type="primary"):
            data.kill(False)
            st.rerun()
    else:
        if st.button("Engage kill switch"):
            data.kill(True)
            st.rerun()
    st.caption(f"store: {view['store_kind']} · broker: {view['broker']} · ${view['notional_per_side']:,.0f} per side")

if auto:
    @st.fragment(run_every=30)
    def _tick():
        st.rerun()
    _tick()

st.title("Paid to hold the bag")
st.caption(f"VIX-gated opening-auction gap fade · session {session} · threshold VIX {view['vix_threshold']:g}")

tab_live, tab_session, tab_research, tab_replay = st.tabs(["Today", "Session detail", "Research", "Replay"])

# ---------------------------------------------------------------- today
with tab_live:
    g = view["gate"]
    hist = view["history"]
    traded = hist[hist["gate_on"].astype(bool)] if len(hist) else hist
    tiles = [
        ("Gate", ("ON" if g["on"] else "OFF") if g else "—", (g["source"] if g else "pre-open has not run")),
        ("VIX (t−1)", f"{g['vix']:.2f}" if g else "—", f"as of {g['vix_as_of']}" if g else None),
        ("VIX / VIX3M", f"{g['vix']/g['vix3m']:.3f}" if g and g["vix3m"] else "—",
         ("backwardation" if g["vix"] > g["vix3m"] else "contango") if g and g["vix3m"] else ("no VIX3M" if g else None)),
        ("Universe", f"{g['n_universe']} names" if g else "—", None),
        ("Net, traded sessions", f"${traded['net_pnl'].sum():+,.0f}" if len(traded) else "—",
         f"{len(traded)} sessions, mean {_bps(traded['net_bps'].mean())} bps" if len(traded) else None),
    ]
    for col, (label, value, delta) in zip(st.columns(5), tiles):
        col.metric(label, value, delta)

    if g:
        st.info(g["reason"]) if g["on"] else st.warning(g["reason"])

    left, right = st.columns([3, 2])
    with left:
        st.subheader("P&L by session")
        if len(hist):
            st.line_chart(hist.set_index("session_date")[["cum_net"]].rename(columns={"cum_net": "cumulative net, $"}), height=220)
            show = hist[["session_date", "gate_on", "vix_lag", "gross_bps", "cost_bps", "net_bps", "realised_spread_bps",
                         "basket_overlap", "shortfall_bps", "net_pnl"]].copy()
            show["gate_on"] = show["gate_on"].map(lambda x: "ON" if x else "off")
            show["basket_overlap"] = show["basket_overlap"].map(lambda x: None if pd.isna(x) else f"{x:.0%}")
            st.dataframe(show.rename(columns={"session_date": "date", "gate_on": "gate", "vix_lag": "VIX−1",
                                              "gross_bps": "gross bps", "cost_bps": "cost bps", "net_bps": "net bps",
                                              "realised_spread_bps": "rule book bps", "basket_overlap": "overlap",
                                              "shortfall_bps": "shortfall bps", "net_pnl": "net $"}),
                         hide_index=True, width="stretch",
                         column_config={"date": st.column_config.DateColumn(),
                                        "gross bps": st.column_config.NumberColumn(format="%.1f"),
                                        "cost bps": st.column_config.NumberColumn(format="%.1f"),
                                        "net bps": st.column_config.NumberColumn(format="%+.1f"),
                                        "rule book bps": st.column_config.NumberColumn(format="%+.1f"),
                                        "shortfall bps": st.column_config.NumberColumn(format="%+.1f"),
                                        "net $": st.column_config.NumberColumn(format="$%+,.0f"),
                                        "VIX−1": st.column_config.NumberColumn(format="%.2f")})
        else:
            st.info("No sessions recorded yet. Use the Replay tab to run a past session, or wait for the scheduler.")
    with right:
        st.subheader("Steps today")
        if len(view["steps"]):
            st.dataframe(view["steps"][["step", "status", "ts"]], hide_index=True, width="stretch")
        else:
            st.caption("No steps recorded for this session.")
        st.subheader("Risk events")
        ev = view["risk_events"]
        if len(ev):
            for r in ev.head(8).itertuples():
                (st.error if r.level == "block" else st.warning)(f"{str(r.ts)[:16]} · {r.step}/{r.check_name} — {r.message}")
        else:
            st.caption("None.")

    st.subheader("Positions")
    pos = view["positions"]
    if len(pos):
        marked, err = data.marks(feed(), pos)
        if err:
            st.warning(f"marks unavailable: {err}")
        gross = (marked["qty"].abs() * marked["avg_price"]).sum()
        m1, m2, m3 = st.columns(3)
        m1.metric("Names", f"{(marked['qty'] > 0).sum()} long / {(marked['qty'] < 0).sum()} short")
        m2.metric("Gross", f"${gross:,.0f}")
        if "mark_pnl" in marked:
            pnl = marked["mark_pnl"].sum()
            m3.metric("Marked P&L", f"${pnl:+,.0f}", f"{pnl/gross:.2%} of gross" if gross else None)
        st.dataframe(marked.sort_values("notional", ascending=False), width="stretch",
                     column_config={"avg_price": st.column_config.NumberColumn(format="$%.2f"),
                                    "last": st.column_config.NumberColumn(format="$%.2f"),
                                    "notional": st.column_config.NumberColumn(format="$%,.0f"),
                                    "mark_pnl": st.column_config.NumberColumn(format="$%+,.0f")})
    else:
        st.caption("Flat. The book holds nothing overnight, and nothing at all on days the gate is off.")

# ---------------------------------------------------------------- session
with tab_session:
    st.subheader(f"Targets and orders · {session}")
    tgt = view["targets"]
    if len(tgt):
        a, b = st.columns(2)
        a.metric("Long leg", f"{(tgt['side'] == 1).sum()} names", f"${(tgt.loc[tgt['side'] == 1, 'target_notional']).sum():,.0f}")
        b.metric("Short leg", f"{(tgt['side'] == -1).sum()} names", f"${-(tgt.loc[tgt['side'] == -1, 'target_notional']).sum():,.0f}")
        st.dataframe(tgt[["est_gap_bps", "relgap", "pct_rank", "side", "target_qty", "target_notional", "est_source"]]
                     .sort_values("relgap"), width="stretch",
                     column_config={"est_gap_bps": st.column_config.NumberColumn("est. gap bps", format="%+.0f"),
                                    "relgap": st.column_config.NumberColumn(format="%+.4f"),
                                    "pct_rank": st.column_config.NumberColumn(format="%.3f"),
                                    "target_notional": st.column_config.NumberColumn(format="$%,.0f")})
    else:
        st.caption("No signal recorded for this session (gate off, or pre-open not run).")
    od = view["orders"]
    if len(od):
        st.dataframe(od[["ts", "symbol", "side", "qty", "order_type", "status", "broker", "note"]], hide_index=True, width="stretch")

# ---------------------------------------------------------------- research
with tab_research:
    st.subheader("The research behind the rule")
    st.caption("Committed results from the pre-registered study. These do not change when the paper book trades.")
    rv = research()
    q = rv["vix_quintiles"]
    if q is not None:
        st.markdown("**Gross gap-fade spread by lagged-VIX quintile, in-sample (2005–2024).** The participation rule trades only when yesterday's VIX ≥ 20, which is roughly the top quintile.")
        st.bar_chart(q.set_index("vix_quintile")[["mean_bps"]].rename(columns={"mean_bps": "mean spread, bps/day"}), height=240)
        st.dataframe(q[["vix_quintile", "vix_lo", "vix_hi", "mean_bps", "se_bps", "ann_sharpe", "n_days"]], hide_index=True, width="stretch",
                     column_config={"mean_bps": st.column_config.NumberColumn("mean bps/day", format="%.1f"),
                                    "se_bps": st.column_config.NumberColumn("s.e.", format="%.2f"),
                                    "ann_sharpe": st.column_config.NumberColumn("gross Sharpe", format="%.2f"),
                                    "vix_lo": st.column_config.NumberColumn(format="%.1f"),
                                    "vix_hi": st.column_config.NumberColumn(format="%.1f")})
    figs = rv["figures"]
    if figs:
        st.markdown("**Figures from the note**")
        choice = st.selectbox("Figure", [f.name for f in figs], index=next((i for i, f in enumerate(figs) if "gapfade_equity_full" in f.name), 0))
        st.image(str(next(f for f in figs if f.name == choice)), width="stretch")
    panel = rv["panel"]
    if panel is not None:
        st.markdown("**Daily gross spread of the rule's book (bps), full sample.** The dashed line is the VIX threshold; markers are the sessions the paper book has replayed.")
        spread = (1e4 * panel.set_index("date")["spread_q"]).rename("gross spread bps")
        st.line_chart(spread.rolling(21).mean().rename("21-day mean, bps/day"), height=220)
        if len(hist):
            replayed = spread.reindex(pd.to_datetime(hist["session_date"]))
            st.caption(f"{len(hist)} replayed sessions vs the full-sample distribution: replayed mean {replayed.mean():+.1f} bps, full-sample mean {spread.mean():+.1f} bps.")

# ---------------------------------------------------------------- replay
with tab_replay:
    st.subheader("Replay a past session")
    st.caption("Runs the full cycle — gate, indicative prices from Nasdaq auction imbalance, orders, fills at the official prints, P&L, reconciliation — and writes it to the store. Idempotent: a session already recorded is left as is; use reset first to recompute it.")
    d = st.date_input("Session to replay", clock.session_date() - timedelta(days=1), max_value=clock.session_date(), key="replay_date")
    col_a, col_b = st.columns([1, 3])
    with col_a:
        go = st.button("Run replay", type="primary")
        reset = st.button("Reset this session")
    with col_b:
        if reset:
            store().reset_session(d)
            st.success(f"cleared {d}")
        if go:
            with st.spinner(f"replaying {d} (Databento imbalance query included, ~10s)…"):
                try:
                    res = data.replay_session(store(), d)
                    st.success(f"{d}: gate {'ON' if res.get('gate_on') else 'OFF'}, gross {_bps(res.get('gross_bps'))} bps, net {_bps(res.get('net_bps'))} bps, rule book {_bps(res.get('realised_spread_bps'))} bps")
                except Exception as e:  # noqa: BLE001 — surface to the operator, keep the app up
                    st.error(f"{type(e).__name__}: {str(e)[:300]}")
    st.divider()
    st.subheader("Briefing")
    st.caption("Gemini writes a short note from the dashboard numbers. It summarises; it decides nothing.")
    if st.button("Write briefing"):
        with st.spinner("writing…"):
            try:
                from live.briefing import write
                st.write(write(store(), session))
            except Exception as e:  # noqa: BLE001
                st.error(f"{type(e).__name__}: {str(e)[:300]}")
