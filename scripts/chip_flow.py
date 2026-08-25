#!/usr/bin/env python3
"""Calculate wallet-cohort deltas and constant-product AMM scenarios.

Input JSON schema:
{
  "supply": 729960160.0,
  "price_usd": 0.01785,
  "fee": 0.0025,
  "pool": {"token": 47494001.0, "quote": 8344.4},
  "wallets": [
    {"id": "wallet-a", "cohort": "old", "previous": 1000000, "current": 700000},
    {"id": "wallet-b", "cohort": "new", "previous": 0, "current": 2000000},
    {"id": "amm", "cohort": "pool", "previous": 0, "current": 0, "excluded": true}
  ]
}

Every tracked wallet needs an explicit previous and current balance. Query wallets
that dropped out of the current Top list; do not encode a missing wallet as zero.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


def number(value: Any, field: str, *, positive: bool = False) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be numeric")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be numeric") from exc
    if not math.isfinite(result):
        raise ValueError(f"{field} must be finite")
    if positive and result <= 0:
        raise ValueError(f"{field} must be greater than zero")
    if not positive and result < 0:
        raise ValueError(f"{field} must not be negative")
    return result


def cohort_summary(rows: list[dict[str, Any]], price_usd: float | None) -> dict[str, Any]:
    previous = sum(row["previous"] for row in rows)
    current = sum(row["current"] for row in rows)
    additions = sorted(
        (
            {"id": row["id"], "amount": row["current"] - row["previous"]}
            for row in rows
            if row["current"] > row["previous"]
        ),
        key=lambda item: item["amount"],
        reverse=True,
    )
    reductions = sorted(
        (
            {"id": row["id"], "amount": row["previous"] - row["current"]}
            for row in rows
            if row["current"] < row["previous"]
        ),
        key=lambda item: item["amount"],
        reverse=True,
    )
    gross_additions = sum(item["amount"] for item in additions)
    gross_reductions = sum(item["amount"] for item in reductions)
    result: dict[str, Any] = {
        "wallet_count": len(rows),
        "previous": previous,
        "current": current,
        "gross_additions": gross_additions,
        "gross_reductions": gross_reductions,
        "net": current - previous,
        "additions": additions,
        "reductions": reductions,
        "full_exits": [row["id"] for row in rows if row["previous"] > 0 and row["current"] == 0],
        "unchanged": [row["id"] for row in rows if row["previous"] == row["current"]],
    }
    if price_usd is not None:
        result["current_value_usd"] = current * price_usd
        result["net_value_at_current_price_usd"] = (current - previous) * price_usd
    return result


def amm_scenarios(
    pool: dict[str, Any], fee: float, sell_sizes: list[float], buy_sizes: list[float]
) -> dict[str, Any]:
    x = number(pool.get("token"), "pool.token", positive=True)
    y = number(pool.get("quote"), "pool.quote", positive=True)
    result: dict[str, Any] = {"token_reserve": x, "quote_reserve": y, "fee": fee}

    sells = []
    for q in sell_sizes:
        q = number(q, "sell size", positive=True)
        effective = q * (1 - fee)
        ratio = (x / (x + effective)) ** 2
        quote_out = y - (x * y) / (x + effective)
        sells.append(
            {
                "token_in": q,
                "quote_out_approx": quote_out,
                "price_ratio": ratio,
                "price_change_pct": (ratio - 1) * 100,
            }
        )
    result["sell_scenarios"] = sells

    buys = []
    for q in buy_sizes:
        q = number(q, "buy size", positive=True)
        if q >= x:
            raise ValueError("buy size must be smaller than the token reserve")
        effective_quote = (x * y) / (x - q) - y
        gross_quote = effective_quote / (1 - fee)
        ratio = (x / (x - q)) ** 2
        buys.append(
            {
                "token_out": q,
                "quote_in_approx": gross_quote,
                "price_ratio": ratio,
                "price_change_pct": (ratio - 1) * 100,
            }
        )
    result["buy_scenarios"] = buys
    return result


def analyze(
    data: dict[str, Any], sell_sizes: list[float], buy_sizes: list[float]
) -> dict[str, Any]:
    supply = number(data.get("supply"), "supply", positive=True)
    price_raw = data.get("price_usd")
    price_usd = None if price_raw is None else number(price_raw, "price_usd")
    fee = number(data.get("fee", 0.0), "fee")
    if fee >= 1:
        raise ValueError("fee must be a fraction smaller than one")

    raw_wallets = data.get("wallets")
    if not isinstance(raw_wallets, list) or not raw_wallets:
        raise ValueError("wallets must be a non-empty list")

    ids: set[str] = set()
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for index, raw in enumerate(raw_wallets):
        if not isinstance(raw, dict):
            raise ValueError(f"wallets[{index}] must be an object")
        wallet_id = str(raw.get("id", "")).strip()
        if not wallet_id:
            raise ValueError(f"wallets[{index}].id is required")
        if wallet_id in ids:
            raise ValueError(f"duplicate wallet id: {wallet_id}")
        ids.add(wallet_id)
        if raw.get("previous") is None or raw.get("current") is None:
            raise ValueError(f"{wallet_id} needs explicit previous and current balances")
        if raw.get("excluded", False):
            continue
        cohort = str(raw.get("cohort", "unclassified")).strip() or "unclassified"
        grouped[cohort].append(
            {
                "id": wallet_id,
                "previous": number(raw["previous"], f"{wallet_id}.previous"),
                "current": number(raw["current"], f"{wallet_id}.current"),
            }
        )

    cohorts = {
        name: cohort_summary(rows, price_usd) for name, rows in sorted(grouped.items())
    }
    for summary in cohorts.values():
        summary["previous_pct_supply"] = summary["previous"] / supply * 100
        summary["current_pct_supply"] = summary["current"] / supply * 100
        summary["pct_point_change"] = (
            summary["current_pct_supply"] - summary["previous_pct_supply"]
        )

    included = [row for rows in grouped.values() for row in rows]
    output: dict[str, Any] = {
        "supply": supply,
        "price_usd": price_usd,
        "tracked": cohort_summary(included, price_usd),
        "cohorts": cohorts,
        "notes": [
            "Cohort identity depends on the input labels; the script does not infer retail, project, or common ownership.",
            "AMM results are constant-product approximations and do not identify the actor behind a trade.",
        ],
    }
    if data.get("pool") is not None:
        output["amm"] = amm_scenarios(data["pool"], fee, sell_sizes, buy_sizes)
    return output


def self_test() -> None:
    fixture = {
        "supply": 100_000_000,
        "price_usd": 0.02,
        "fee": 0.0025,
        "pool": {"token": 10_000_000, "quote": 2_000},
        "wallets": [
            {
                "id": "old-a",
                "cohort": "old",
                "previous": 5_000_000,
                "current": 4_000_000,
            },
            {
                "id": "old-b",
                "cohort": "old",
                "previous": 2_000_000,
                "current": 2_500_000,
            },
            {
                "id": "new-a",
                "cohort": "new",
                "previous": 0,
                "current": 3_000_000,
            },
            {
                "id": "pool",
                "cohort": "pool",
                "previous": 0,
                "current": 0,
                "excluded": True,
            },
        ],
    }
    result = analyze(fixture, [1_000_000], [1_000_000])
    assert result["cohorts"]["old"]["net"] == -500_000
    assert result["cohorts"]["new"]["net"] == 3_000_000
    assert round(result["cohorts"]["new"]["current_pct_supply"], 6) == 3.0
    assert result["amm"]["sell_scenarios"][0]["price_change_pct"] < 0
    assert result["amm"]["buy_scenarios"][0]["price_change_pct"] > 0
    print("self-test ok")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", type=Path, help="JSON snapshot file")
    parser.add_argument(
        "--sell-size", type=float, action="append", default=[], help="token sale size; repeatable"
    )
    parser.add_argument(
        "--buy-size", type=float, action="append", default=[], help="token purchase size; repeatable"
    )
    parser.add_argument("--self-test", action="store_true", help="run built-in checks")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return 0
    if args.input is None:
        parser.error("input is required unless --self-test is used")

    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
        result = analyze(data, args.sell_size, args.buy_size)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
