---
name: analyze-meme-coin-capital-flow
description: Analyze a Solana meme or event coin from its CA using live market data, wallet-level balance changes, funding paths, and AMM math to explain who is buying and selling, whether chips are concentrating or distributing, whether a new operator may be accumulating, and which observable conditions determine the next price paths. Use for questions about capital flow, chip structure, whales, fresh wallets, bots, project wallets, accumulation, distribution, or following the money; do not use for narrative-only or media-heat research.
---

# Meme Coin Capital Flow Analysis

## Purpose

Turn noisy on-chain evidence into an investor-usable answer:

- who actually reduced and increased holdings;
- whether old holders are distributing or merely rotating;
- whether new whales are directional buyers, bots, market makers, or possible coordinated operators;
- whether chips are moving toward strong hands or dispersing to long-tail wallets;
- what must happen next for accumulation, a second pump, or breakdown to be confirmed.

For reflexive event coins, use the causal model `capital pushes price -> price creates attention -> attention legitimizes the narrative -> more capital follows`. Analyze capital first. If the user separately asks about the real-world story, social spread, or media heat, use the event-narrative skill for that branch and keep its conclusions separate from on-chain conclusions.

## Non-negotiable Evidence Rules

1. **Changes matter more than snapshots.** Compare at least two timestamped snapshots. A current Top list alone cannot show who bought or sold.
2. **Track the same old cohort.** Re-query every address from the earlier cohort even if it falls out of the current Top list. Never treat absence from Top holders as a zero balance.
3. **Behavior is not identity.** `fresh`, `organic`, `bot`, `smart money`, wallet age, or transaction style do not prove retail, project ownership, or a common controller.
4. **Organic volume is not retail volume.** Manual whales may be organic; coordinated wallets may also pass heuristic filters.
5. **A relayer, solver, co-signer, exchange withdrawal, or common public service is not common-owner proof.** Require additional funding, timing, sizing, signer, or transfer evidence.
6. **Pool reserve changes quantify aggregate order flow and price impact, not the seller's identity.** Do not use the tautology `price fell -> pool token reserve rose` as the answer to who sold.
7. **Exclude infrastructure.** Remove AMM pools, LP vaults, lockers, CEX custody accounts, bridges, relayers, and public service wallets from holder concentration and directional-whale cohorts where identifiable.
8. **Do not call the residual “retail.”** After accounting for pools and known cohorts, label the remainder `unattributed long-tail and mid-size holders` unless wallet-level evidence supports a narrower identity.
9. **Do not infer project ownership from synchronized behavior alone.** State `possible coordinated operator` until a direct project funding, signer, control, or transfer link exists.
10. **Use absolute timestamps and a cutoff.** Live crypto facts decay quickly. Refresh current data before answering and identify the comparison baseline.

## Evidence Levels

Keep these explicit:

- **Confirmed:** balance deltas, swaps, token/SOL/USDC received, first activity, transaction count, direct funding, common signer, known service label.
- **Strong behavioral inference:** repeated same-second buys, TWAP-like tranches, large spaced manual buys, holding through a drawdown, synchronized first funding plus matching execution.
- **Hypothesis:** new dealer, hidden project wallet, coordinated price defense, retail behavior.
- **Unknown:** beneficial owner and off-chain coordination without direct evidence.

Do not turn a hypothesis into an exact percentage. If the user demands a project/retail/dealer split, provide a clearly labeled estimate or range, list the observable components, and keep an `unknown` bucket.

## Live Data Collection

Confirm the chain, mint, supply, creator, pools, and current market first. Prefer primary or live endpoints and cross-check material values:

- Jupiter asset data: `https://datapi.jup.ag/v1/assets/search?query={CA}`
- RugCheck report: `https://api.rugcheck.xyz/v1/tokens/{CA}/report`
- Solana JSON-RPC methods: `getTokenLargestAccounts`, `getTokenAccountBalance`, `getSignaturesForAddress`, and `getTransaction`

Providers and schemas can change; inspect the response rather than assuming old fields still exist. If an indexed RPC is rate-limited, use another public provider or query already-known token accounts individually. Do not silently substitute stale search snippets for live values.

Capture for both baseline and current snapshots:

- price, market cap, circulating supply, liquidity, holder count;
- buy and sell value, counts, and traders over 5m, 1h, 6h, and 24h;
- Top-holder owner addresses and balances, with pools identified;
- Top-holder concentration, bot holding percentage, bundler holding percentage when available;
- main and material secondary pool reserves;
- balances of the fixed prior whale cohort, including addresses no longer in Top holders.

For every wallet that changes the conclusion, inspect:

- first visible activity and transaction count;
- initial funding source and whether it is a public service;
- token-account transaction sequence and exact balance deltas;
- whether reductions are sales, transfers, liquidity deposits, or consolidation;
- whether buys are one-off, TWAP-like, high-frequency inventory, or large manually spaced tranches;
- whether it holds, adds, or distributes during price stress and rebounds.

## Cohort Accounting

Always calculate two different comparisons.

### Fixed old cohort

Use the same addresses from the earlier snapshot:

- gross additions;
- gross reductions;
- net change;
- full exits;
- unchanged core holders.

This answers whether the original large-holder group is distributing.

### Current concentration cohort

Compare the current Top N total and percentage with the earlier Top N, even though members may differ. This answers whether chips are becoming more concentrated.

The two results can diverge. For example, the old cohort may net sell while Top N concentration rises because new whales replaced the sellers. Call this `whale rotation` or `potential change of control`, not broad distribution.

Use `scripts/chip_flow.py` when explicit previous/current balances and pool reserves are available. Include all fixed old-cohort addresses and query missing current balances before running it.

## Wallet Roles

Classify by observed behavior, not by flattering labels:

- **Original core giant:** early large position, low turnover, unchanged or adding through volatility.
- **Old momentum or mid-size whale:** held before the latest move and now reduces or fully exits.
- **New strategic whale:** newly appears, accumulates meaningful supply, and retains it through a drawdown or rebound.
- **Automated accumulator:** many self-signed tranches or same-second executions, but relatively persistent inventory.
- **Market-making or arbitrage inventory:** extreme transaction frequency and rapidly fluctuating inventory; do not count it as conviction.
- **Possible coordinated operator:** multiple wallets share non-public funding, synchronized creation, matching sizes and timing, and common execution behavior.
- **Project-linked wallet:** direct, traceable creator/project funding or control evidence. Keep this separate from possible coordination.
- **Unattributed long tail:** all unclassified smaller and mid-size holders. Do not automatically call them retail.

A fresh wallet with a large scripted position may be a new operator, an independent whale, or an execution wallet. A mature low-transaction wallet may still be controlled by a professional. Wallet age alone decides neither.

## Reading Price and Flow Together

Use these combinations as hypotheses to test:

- `price down + Top concentration up`: new strong hands may be absorbing broader selling; possible accumulation or change of control.
- `price down + concentration down`: broad risk-off or distribution.
- `price up + driver balances up or stable`: expansion, provided new money is retained.
- `price up + old or driver balances down`: likely distribution into attention.
- `many buy transactions + larger sell value`: smaller tickets are buying while fewer or larger sellers dominate; this does not mean “retail is selling.”
- `holder count up + whales flat`: participation breadth increased, not necessarily capital strength.
- `holder count down + concentration up`: weaker or smaller holders may be exiting while larger wallets absorb; identity remains unattributed.

Always identify both sides. If everyone described is selling but price did not collapse, the analysis is missing the absorber.

## Accumulation and “New Dealer” Test

Treat `new dealer accumulating` as a tradable hypothesis, not an identity fact.

Evidence that strengthens it:

- fresh large wallets accumulate enough to influence the main pool;
- Top concentration rises while price is weak;
- the new wallets retain holdings during a second sell wave;
- they add on stress and do not sell the first rebound;
- older core giants remain locked;
- price eventually stops making new lows despite continued residual selling.

Evidence that weakens or falsifies it:

- the new wallets reduce materially on the first rebound;
- inventory belongs mainly to a high-frequency market maker;
- Top concentration falls with price;
- the alleged drivers stop adding and become trapped supply;
- no price response appears despite repeated net buying;
- transfers reveal mere wallet reshuffling rather than market purchases.

Define materiality relative to supply, pool depth, and the alleged dealer cohort. A useful warning is a 15–20% reduction in the candidate cohort or a sale large enough to move the main pool materially; do not hardcode one token count for every coin.

## AMM Simulation

Use constant-product math only to quantify sensitivity and scenario triggers. For token reserve `x`, quote reserve `y`, fee fraction `f`, and token sale `q`, an approximation is:

`price_after / price_before ~= (x / (x + q * (1 - f)))^2`

For buying exactly `q` tokens from the pool:

`price_after / price_before ~= (x / (x - q))^2`

`effective_quote_in = x * y / (x - q) - y`

`gross_quote_in ~= effective_quote_in / (1 - f)`

State that multi-pool routing, arbitrage, concentrated liquidity, fees, LP actions, and concurrent traders make this a scenario model, not an execution quote. Use it to say what another 5M-token sell could do, not to identify who sold.

## Forecasting the Next Path

Lead with one base judgment, then give bull and bear alternatives with observable triggers.

For a “funds fast train,” require the feedback loop, not merely a green candle:

- candidate driver wallets are net accumulating or holding;
- old core holders are not distributing;
- net capital flow and price-impact efficiency improve;
- a local breakout holds while the driver cohort retains its position.

A rally is suspect when volume rises but price response weakens, or when candidate drivers sell into the move. A decline may be accumulation when concentration rises and candidate drivers retain or add, but it is not confirmed until selling stops moving price lower.

Use probability-weighted paths only as judgment, never as fact. Each path needs:

- price or market-cap zone;
- wallet-flow trigger;
- invalidation condition;
- relevant time horizon.

## Output Shape

Keep the answer compact and decision-oriented:

1. **One-sentence conclusion:** accumulation, distribution, whale rotation, or insufficient evidence.
2. **What changed:** baseline versus current market, holder, and concentration metrics.
3. **Who sold:** fixed-cohort gross and net reductions, with the material wallets.
4. **Who bought:** new and existing accumulators, excluding infrastructure and unstable bot inventory.
5. **What happened:** explain how the buyers and sellers produced the observed price path.
6. **Dealer/project/retail judgment:** confirmed facts, behavioral inference, and unknown ownership.
7. **Next path:** base, bull, and bear triggers plus the wallet balances that invalidate the view.

Never bury the conclusion under transaction dumps. Do not repeat obvious pool mechanics as filler. When correcting an earlier view, state exactly which new balance or transaction changed the conclusion.
