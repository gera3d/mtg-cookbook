# Recipe: Build a Budget Commander Deck

## Outcome

Produce a Commander deck that is exactly 100 cards, legal for the chosen commander, aligned to the player's plan, and quoted from live marketplace inventory without hiding constraints or checkout costs.

This recipe deliberately separates four different things that are often mashed together: building the list, validating it, pricing it, and placing an order.

## The brief

Collect this before building:

| Input | Example |
| --- | --- |
| Commander and colors | `Kratos, God of War` / its printed color identity |
| Power goal | Casual, upgraded precon, high-power casual, or a specific pod |
| Game plan | Combat, sacrifice, spellslinger, artifacts, tokens, etc. |
| Spend ceiling | $35 for cards, excluding checkout fees |
| Already owned | Commander and basic lands supplied |
| Marketplace constraints | English only; at least lightly played; nonfoil; US region; CardTrader Zero |
| Must-plays / exclusions | Named cards, mechanics, or cards not to use |

If the player says "cheapest," make the unspoken choices visible. Cheaper listings can be non-English, poor condition, out of region, or part of a slower service. Do not silently pick them.

## Build the deck by role

Start with a role map, then choose cards:

- **Mana:** lands, rocks, ramp, and fixing that support the commander.
- **Card flow:** draw, filtering, recursion, or repeatable engines.
- **Interaction:** removal, artifact/enchantment answers, protection, and board wipes when the deck needs them.
- **Primary plan:** the cards that make the commander and strategy work.
- **Finishers:** ways to turn the board state into a win.

Maintain one exact decklist. A Commander deck is 100 cards including its commander, and other cards must follow singleton and color-identity rules unless an actual card rule creates an exception.

Run the included validator before claiming completion:

```bash
python3 skills/magic-deck-api-builder/scripts/validate_commander.py decklist.txt
```

The script catches deterministic count and duplicate issues. Verify color identity, commander legality, and rules text against current card data as a separate live check.

## Give a useful strength rating

A number without an explanation is not useful. State the assumed pod, the deck's realistic turn profile, its strongest lines, and its weaknesses.

Example:

> **6/10 — upgraded casual.** It advances its plan consistently, has enough interaction to participate, and can close through combat. It does not have fast mana, dense tutoring, or compact deterministic combos, so it is not intended for cEDH tables.

That tells the player whether the deck belongs at their table. It is an estimate, not a universal fact.

## Quote the live inventory

Build a normalized quote for every selected listing:

| Field | Why it matters |
| --- | --- |
| Card and printing | Prevents accidental substitutions |
| Language | Enforces English-only or another stated filter |
| Condition and foil state | Makes the actual product clear |
| Seller/service and readiness | Explains delivery tradeoffs |
| Item price | Computes the article subtotal |
| Quote time | Inventory and prices move |

Report these totals separately:

1. Article subtotal.
2. Marketplace or service fees.
3. Shipping.
4. Tax, if the marketplace displays it.
5. Final checkout total.

If cards are being consolidated through CardTrader Zero, distinguish "arrived at the hub" from "shipped to the player." Those are different delivery milestones.

## Create the gallery

Use the Skill's example schema to make a deck page a player can scan:

```bash
python3 skills/magic-deck-api-builder/scripts/render_gallery.py deck-data.json --out deck-gallery.html
```

The output groups cards by role, includes the price quote and constraints, copies the exact list, and retrieves card art and rules text when the player hovers, focuses, or clicks a card.

Label the gallery with its quote timestamp, filters, supplied cards, and exclusions. A polished gallery should make the limitations clearer, not hide them.

## The purchase gate

Generating the list and quote is preparation. Adding items to a cart, accepting condition/language substitutions, entering checkout, and paying are state changes.

Immediately before the final payment button, present:

- Exact item count and supplied cards/lands.
- Confirmed language, condition, foil, and printing constraints.
- Article subtotal, every displayed fee, shipping, tax status, and final total.
- Any missing cards, substitutions, or delivery wait tradeoffs.

Then obtain a fresh confirmation that names the marketplace and charge. A previous general "buy it" does not cover a changed total, a mixed-language warning, or a different card count.

## Deliverable checklist

- [ ] Exact Commander decklist validated for 100 cards and singleton structure.
- [ ] Live rules and color-identity check completed.
- [ ] Plain-language game plan and strength estimate included.
- [ ] English/condition/foil/region filters stated and enforced.
- [ ] Live per-card quote timestamped.
- [ ] Fees, shipping, tax, and final total separated from card subtotal.
- [ ] Interactive gallery generated.
- [ ] Fresh final confirmation obtained before any payment.

