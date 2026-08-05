# Card data and pricing

## Source boundary

Use a card-data source for rules, type lines, mana value, color identity, legality, and images. Scryfall is a good public source; resolve a named card only after normalizing its name and keep the source response separate from marketplace data.

Use a marketplace adapter for stock and price. The adapter belongs to the target harness, never to this Skill. It may use an existing connector, an authenticated browser session the owner explicitly put in scope, or a named read-only secret-broker action. Do not embed a token, cookie, address, payment method, or user-specific API configuration.

## Required quote fields

Normalize every selected listing to this minimum shape:

```json
{
  "name": "Example Card",
  "quantity": 1,
  "printing": "Example Set #123",
  "language": "en",
  "condition": "Slightly Played",
  "foil": false,
  "service": "CardTrader Zero",
  "seller": "optional seller label",
  "item_price": 0.25,
  "ready_estimate": "optional estimate",
  "checked_at": "2026-08-05T20:00:00Z"
}
```

Keep a separate quote summary:

```json
{
  "article_subtotal": 15.99,
  "service_or_payment_fee": 1.17,
  "shipping_to_hub": 0.0,
  "shipping_to_owner": null,
  "tax": null,
  "checkout_total": 17.16,
  "currency": "USD",
  "checked_at": "2026-08-05T20:00:00Z"
}
```

Use `null` for an unquoted component. Never present an article subtotal as a final charge.

## Pricing decisions

1. Apply hard constraints before sorting: language, condition, foil, printing match, service, and region.
2. Explicitly distinguish the cheapest raw listing from the cheapest eligible listing. A low raw listing can disappear after language, condition, seller, or service filters.
3. Mark data as stale whenever the page or API quote is older than the current shopping session. Re-query immediately before cart preparation.
4. When a desired card is unavailable, name it, show the impact on deck count and total, and propose a replacement or ask the owner. Never silently drop it.
5. Keep price optimization separate from deck quality. Do not cut essential mana, interaction, or a required build-around only because it is the most expensive card without explaining the tradeoff.
