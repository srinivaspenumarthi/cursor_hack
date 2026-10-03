"""Configuration: credentials from .env (never committed), sizing and risk limits."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

# Pre-registered rule constants (HYPOTHESIS_B.md) — imported here so the live layer
# cannot drift from the research code silently.
import sys  # noqa: E402

sys.path.insert(0, str(ROOT / "src"))
from gqh.gapfade import C_BASE_BPS, GAP_FILTER, MIN_NAMES, VIX_THRESHOLD  # noqa: E402


def _f(name: str, default: float) -> float:
    return float(os.environ.get(name, default))


def _i(name: str, default: int) -> int:
    return int(os.environ.get(name, default))


@dataclass
class Settings:
    # credentials
    massive_api_key: str | None = os.environ.get("MASSIVE_API_KEY") or None
    databento_api_key: str | None = os.environ.get("DATABENTO_API_KEY") or None
    gemini_api_key: str | None = os.environ.get("GEMINI_API_KEY") or None
    gemini_model: str = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    database_url: str | None = os.environ.get("DATABASE_URL") or None
    alpaca_api_key: str | None = os.environ.get("ALPACA_API_KEY") or None
    alpaca_api_secret: str | None = os.environ.get("ALPACA_API_SECRET") or None
    alpaca_base_url: str = os.environ.get("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")

    # strategy (pre-registered; do not tune here)
    vix_threshold: float = VIX_THRESHOLD
    n_buckets: int = 5
    gap_filter: float = GAP_FILTER
    min_names: int = MIN_NAMES
    c_base_bps: float = C_BASE_BPS

    # sizing
    notional_per_side: float = _f("LIVE_NOTIONAL_PER_SIDE", 1_000_000.0)
    min_price: float = _f("LIVE_MIN_PRICE", 5.0)

    # risk limits
    max_gross_notional: float = _f("LIVE_MAX_GROSS", 2 * _f("LIVE_NOTIONAL_PER_SIDE", 1_000_000.0) * 1.10)
    max_name_pct_of_side: float = _f("LIVE_MAX_NAME_PCT", 0.025)
    # same-day disaster stop (marked P&L / gross). The book's daily std at VIX 25-30 is ~1.5% of
    # gross, so 5% is a >3-sigma event, not a normal bad day.
    daily_loss_limit_pct: float = _f("LIVE_DAILY_LOSS_LIMIT_PCT", 0.05)
    review_drawdown_pct: float = _f("LIVE_REVIEW_DRAWDOWN_PCT", 0.03)   # trailing 5 sessions -> warn only
    stale_vix_days: int = _i("LIVE_STALE_VIX_DAYS", 4)
    max_indicative_age_s: int = _i("LIVE_MAX_INDICATIVE_AGE_S", 180)
    databento_cost_cap_usd: float = _f("LIVE_DATABENTO_COST_CAP", 0.25)

    # paths
    root: Path = ROOT
    sqlite_path: Path = ROOT / "live" / "state" / "live.sqlite"
    kill_switch: Path = ROOT / "live" / "KILL"
    universe_csv: Path = ROOT / "data" / "sp500_constituents.csv"
    cache_dir: Path = ROOT / "data" / "raw"

    extra: dict = field(default_factory=dict)

    @property
    def paper(self) -> bool:
        return not (self.alpaca_api_key and self.alpaca_api_secret)


SETTINGS = Settings()
