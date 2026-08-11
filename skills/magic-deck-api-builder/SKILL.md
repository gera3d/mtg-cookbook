---
name: magic-deck-api-builder
description: Build, validate, price, and present Magic: The Gathering decks—especially budget Commander decks—using card-data APIs and marketplace adapters. Use when asked to design a deck around a commander, optimize for a budget or card constraints, verify a 100-card list, collect live prices from CardTrader or another marketplace, create a card-hover deck gallery, or prepare (but not automatically place) a card order.
---

# Magic Deck API Builder

Build decision-ready decks: a legal list, a truthful live-price quote, and a useful presentation. Keep card rules, marketplace pricing, and purchasing actions separate.

## Start with a deck brief

Capture these inputs before pricing:

- Format, commander, color identity, and intended power band.
- Strategy, must-include cards, cards already owned, and budget ceiling.
- Marketplace constraints: language, minimum condition, foil treatment, region, and service (for example, CardTrader Zero).
- Whether basic lands and the commander are supplied or must be purchased.

Do not silently turn “cheapest” into mixed-language or heavily played cards. If no language or condition is stated, use the marketplace default only after labeling it. Treat “English only” as a hard filter, not a preference.

## Build and validate

1. Build by roles first: mana, card flow, interaction, primary plan, and finishers. Explain the deck’s actual win pattern in plain language.
2. Maintain an exact decklist, including supplied cards and basic lands. For Commander, target exactly 100 cards including the commander.
3. Run `scripts/validate_commander.py` before claiming the list is complete. It catches count and singleton mistakes; use a live card-data source to verify color identity, format legality, and current rules text.
4. Read `references/commander-intelligence.md` before producing Commander Game Changers, combo, bracket, or power analysis. Use stable card identities and a versioned official-policy snapshot; never match policy cards by name alone.
5. State the deck-strength score as a reasoned estimate, not an objective rating. Name the evidence, assumed pod, and real limitations.

## Price live marketplace inventory

Read `references/card-data-and-pricing.md` before wiring or using a card-data API or marketplace adapter.

- Re-check price and availability live. Listings disappear and fees change.
- Normalize every candidate into name, printing, language, condition, foil state, seller/service, item price, and readiness estimate.
- Keep **article subtotal**, marketplace/service fees, shipping, tax, and final checkout total as separate fields. A scan total is not a checkout total.
- Do not embed API keys, browser cookies, personal addresses, or payment details in the Skill, scripts, reports, or gallery data. Use an existing named, least-privilege adapter in the target harness.

## Produce the deck gallery

Use `assets/deck-data.example.json` as the schema and run:

```bash
python3 scripts/render_gallery.py deck-data.json --out deck-gallery.html
```

The generated page groups cards by role, shows quoted per-card pricing, gives a deck-strength rationale, copies the exact list, and fetches card art/rules text from Scryfall when a card is hovered, focused, or clicked. Label the gallery’s quote timestamp, filters, supplied cards, and exclusions such as checkout fees.

## Marketplace and purchase boundary

Read `references/cart-and-purchase-gates.md` before modifying a live cart or checkout.

Research, decklists, and galleries are safe preparation. Adding items, clearing a cart, accepting a warning about noncompliant cards, and purchasing are external state changes. Never accept a non-English warning when the brief says English-only. Immediately before the final payment button, report the exact item count, language/condition compliance, total, fees, shipping, and any known wait-time tradeoff, then obtain a fresh confirmation.

## Resources

- `scripts/validate_commander.py` — deterministic deck-size and singleton check.
- `scripts/render_gallery.py` — render a standalone hover-card deck gallery from normalized JSON.
- `references/card-data-and-pricing.md` — API/provider boundary and quote format.
- `references/commander-intelligence.md` — public-source access, Game Changers policy snapshots, combo evidence, and the explainable Commander power contract.
- `references/cart-and-purchase-gates.md` — live-cart and payment safeguards.
- `assets/deck-data.example.json` — minimal portable gallery input.
