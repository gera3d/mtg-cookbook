# Cart and purchase gates

## Research versus state change

Reading listings, building a deck, validating it, and generating a gallery are research. Adding cards, changing a cart, accepting a marketplace compliance warning, entering checkout, and paying are state changes.

Before modifying a cart, reread these facts from the live page:

- Exact card count and decklist match.
- Language, condition, foil, and printing constraints.
- Item subtotal and price timestamp.
- Marketplace service and delivery model.

Do not clear or replace a cart until confirming it contains only the scoped deck. Do not mix an old, noncompliant cart with a refreshed one.

## Language and condition

When the brief says English-only, all selected listings must be `en` before checkout. A marketplace warning about non-English items is a blocker, not permission to continue. Rebuild or replace the noncompliant selection, then verify it again.

Treat card condition as a quoted attribute. “Cheapest” can mean poor or played condition; do not substitute it for near-mint without making that clear.

## Final charge

Immediately before the final payment action, report:

- Exact item count and any supplied cards/lands.
- Language and condition compliance.
- Article subtotal, fees, shipping, tax status, and final displayed total.
- Any missing card, replacement, or wait-time tradeoff.

Then ask for a fresh confirmation that names the marketplace and charge. A prior “buy it” does not replace this action-time confirmation if the total, language, condition, or item count changed.

For CardTrader Zero, do not describe transit to the Hub as delivery to the owner. The owner may later need to initiate the Hub-to-home shipment.
