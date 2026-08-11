# Commander intelligence: public data, Game Changers, and an explainable power estimate

## The decision

Build the first version around **Scryfall**, **Commander Spellbook**, and a small, versioned copy of the official Commander policy. They provide the data needed to make a Commander deck genuinely useful: card facts, legality, known combos, and a reliable Game Changers count.

Do not call a deck's power level an official fact. Commander brackets are a conversation aid, and a useful app should show *why* it made an estimate instead of pretending one number settles the question.

## Provider matrix

Access conditions below were checked on 2026-08-10. Recheck them before a production launch; provider rules and endpoints change.

| Provider | Public access? | Use it for | Do not use it for |
| --- | --- | --- | --- |
| [Scryfall API](https://scryfall.com/docs/api) | Yes; no app credential for ordinary API access | Current Oracle text, card identities, color identity, mana value, legalities, images, printings, and basic price fields | A live marketplace quote or a canonical power score |
| [Commander Spellbook](https://commanderspellbook.com/about/) | Yes; its backend exposes a REST API and is open source | Known Commander combos, prerequisites, outcomes, and combo permalinks | Treating every possible synergy as a guaranteed win |
| [MTGJSON downloads](https://mtgjson.com/getting-started/) | Yes; downloadable data is free and open source | Local/offline card and printing indexes, identifiers, and historic price-data snapshots | Low-latency live-card lookups; its hosted GraphQL service requires a separate access token |
| [Wizards Commander updates](https://magic.wizards.com/en/news/announcements/commander-brackets-beta-update-february-9-2026) | Public page, **not** an API | The official Commander Game Changers and bracket policy | Automatic unreviewed policy changes |
| [CardTrader Full API](https://www.cardtrader.com/en/docs/api/full/reference) | No; an account token is required | The owner's inventory, orders, and authorized marketplace operations | A client-side integration or a public card-data source |
| [TCGplayer API](https://help.tcgplayer.com/hc/en-us/articles/360061115874-TCGplayer-API-Terms-Conditions) | No; written approval is required | An approved, terms-compliant pricing or referral integration | An assumed public price feed or a combined multi-market price database |
| [Cardmarket API](https://help.cardmarket.com/es/cardmarket-api) | No; it is not accepting new access applications | Nothing in a new build until access is actually granted | A dependency for v1 |

Scryfall asks clients to stay under 10 requests per second, send meaningful `User-Agent` and `Accept` headers, cache data, and use bulk downloads for large jobs. Follow that guidance instead of retrying through a rate limit. [Scryfall rate-limit guidance](https://scryfall.com/docs/faqs/i-m-having-trouble-accessing-the-scryfall-api-or-i-m-blocked-17)

## Architecture that keeps the facts straight

```text
Decklist import
  -> Scryfall resolver and cache
  -> deterministic legality and deck-shape checks
  -> Commander Spellbook combo lookup
  -> official-policy snapshot match
  -> explainable score and deck report

Marketplace adapter (optional) -> exact-printing inventory and checkout quote
```

Keep the marketplace adapter beside—not inside—the power engine. A card's current price, seller condition, and checkout availability should never change its legality, Game Changers count, or core power result.

### Keep two card identifiers

Persist both IDs whenever a card is resolved:

```json
{
  "name": "Example Card",
  "scryfall_id": "printing-specific-id",
  "oracle_id": "gameplay-identity-id",
  "set_code": "ABC",
  "collector_number": "123",
  "finish": "nonfoil"
}
```

- Use **`oracle_id`** to match rules-level policies such as Game Changers. Reprints should count as the same gameplay card.
- Use **`scryfall_id`**, set code, collector number, language, and finish when the player cares about an exact printing or a marketplace quote.
- Do not match a Game Changer by display name alone. Names, punctuation, and card faces can make that fragile.

## Scryfall integration

Make server-side requests through a small adapter. The browser sends decklist input to the app; only the adapter calls Scryfall. That gives the app a shared cache, controlled rate limiting, and a consistent error path.

For each resolved card, retain only the fields the analysis needs:

```ts
type ResolvedCard = {
  scryfall_id: string;
  oracle_id?: string;
  name: string;
  mana_cost?: string;
  cmc: number;
  color_identity: string[];
  type_line: string;
  oracle_text?: string;
  legalities: { commander?: string };
  image_uri?: string;
  prices?: { usd?: string | null; usd_foil?: string | null; eur?: string | null };
};
```

Implementation rules:

1. Normalize imported names, but preserve the player's original line for error reporting.
2. Resolve a single card with Scryfall's named-card endpoint. Use the documented collection endpoint or a bulk file for a whole deck or collection—never issue one uncached search per card on every page load.
3. Cache normal card facts for at least a day; invalidate the relevant card cache when a new set or a rules update needs it.
4. Include a useful application `User-Agent` and an `Accept: application/json` header. Throttle below the published limit and respect `429` responses.
5. Record `source: "scryfall"` and `fetched_at` with every analysis. If resolution is incomplete, return an incomplete analysis rather than guessing.

## Commander Spellbook integration

After Scryfall has resolved the deck, pass the normalized card set to Commander Spellbook's documented REST API. Save the returned combo identity, requirements, result, and permalink.

Classify each result explicitly:

| Result | Meaning in the report | Scoring treatment |
| --- | --- | --- |
| Complete combo | Every required card is present and the stated prerequisites can be reviewed | Eligible for the compact-combo component |
| Near combo | The deck has most but not all required cards | Show it as a possible upgrade; do not score it as a win line |
| Illegal or color-incompatible combo | The cards match but the line is not legal for this Commander deck | Show only when troubleshooting; do not score it |
| Unknown | The provider did not return a usable result | Keep the combo component incomplete, not zero |

The app should show the actual Commander Spellbook link and prerequisites. A player needs to know whether a line needs a haste enabler, available mana, a graveyard, or another board condition before calling it a turn-five win.

## Game Changers: a versioned policy snapshot

Wizards publishes Game Changers in Commander-brackets updates, not a stable JSON API. Treat the list as policy data with provenance, not as a hidden hard-coded array.

```json
{
  "policy": "commander-game-changers",
  "source_url": "https://magic.wizards.com/en/news/announcements/commander-brackets-beta-update-february-9-2026",
  "source_published_at": "2026-02-09",
  "reviewed_at": "2026-08-10T00:00:00Z",
  "oracle_ids": ["one-id-per-gameplay-card"]
}
```

Recommended update procedure:

1. Watch the official Commander announcement route for an update.
2. Review the announcement and write down added and removed names.
3. Resolve each name through Scryfall and store its `oracle_id` in a new snapshot.
4. Run deck fixtures against the new snapshot.
5. Publish the new snapshot with its source URL and date; never silently overwrite the old one.

Return both counts so the UI is unambiguous:

```json
{
  "game_changers": {
    "policy_version": "2026-02-09",
    "distinct_cards": 2,
    "copies": 2,
    "includes_commander": false,
    "cards": [
      { "name": "Example Card", "oracle_id": "...", "zone": "mainboard" }
    ]
  }
}
```

For Commander, `distinct_cards` and `copies` will usually agree, but reporting both makes the engine reusable for non-singleton formats and makes the commander treatment visible. The app should also disclose the policy version in every result. Do **not** promise a permanent count: Wizards can change the list.

## An explainable power estimate

The score is a product feature, not an official Commander ruling. Use a 0–100 internal score and display it as a rounded 0–10 estimate only with its evidence.

| Component | Range | Evidence to measure |
| --- | ---: | --- |
| Acceleration | 0–20 | Fast mana, efficient early ramp, and access to colors |
| Consistency | 0–20 | Tutors, card selection, repeatable draw, and commander access |
| Win pressure | 0–25 | Complete compact combos, credible finishers, and expected setup cost |
| Interaction | 0–15 | Efficient answers, board interaction, and free or low-cost protection |
| Mana efficiency | 0–10 | Curve, land count, fixing, and dead-card risk |
| Resilience | 0–10 | Protection, recursion, redundancy, and recovery after a wipe |

Start with a transparent, versioned card-role ruleset. For example, an exact list of recognized fast-mana cards is easier to test and revise than a model guessing from card art. Use Oracle text, mana value, types, and Commander Spellbook evidence to support the classifier. Flag cards the ruleset cannot classify instead of quietly treating them as nothing.

Avoid double-counting. A card that is fast mana and a Game Changer can contribute to acceleration; Game Changers should be a clear policy signal in the report, not an automatic shortcut to a high score.

Return the score as data, then let the interface explain it:

```json
{
  "power": {
    "ruleset_version": "power-v1",
    "score_100": 74,
    "display_score_10": 7.4,
    "confidence": "medium",
    "signals": [
      { "kind": "fast_mana", "count": 4, "points": 10, "cards": ["..."] },
      { "kind": "complete_combo", "count": 1, "points": 14, "source": "Commander Spellbook" },
      { "kind": "game_changer", "count": 2, "points": 0, "note": "Policy signal; not separately scored" }
    ],
    "limitations": ["Four cards could not be resolved", "No play-pattern history supplied"]
  }
}
```

Suggested labels are **low-power casual**, **casual**, **tuned**, **high power**, and **competitive-leaning**. Present them as a starting point for a pregame conversation, never as a claim that the app can guarantee a bracket or a win turn.

## Where AI helps—and where it does not

Use an LLM after the deterministic analysis to:

- explain the score in plain language;
- surface the two or three biggest reasons a deck plays above or below its target pod;
- suggest a replacement and explain the tradeoff; and
- answer questions such as “why did this move from 6.8 to 7.4?”

Do not use an LLM as the source of current legality, Game Changers membership, exact card identity, pricing, or score arithmetic. The answer should be reproducible from the stored source snapshots and analysis version.

## Minimal API contract for the app

```text
POST /api/commander/analyze
  input: commander, mainboard, optional sideboard, selected policy version
  output: resolution errors, legality, game-changers result, combos,
          role counts, power evidence, score, sources, and timestamps
```

The front end should render partial results honestly. For example, if Scryfall resolves 98 of 100 cards, show the two unresolved lines and mark the score as incomplete rather than producing a confident answer.

## Tests that matter before launch

- A deck with zero Game Changers reports zero from a named policy snapshot.
- A deck with reprints of a Game Changer matches once by `oracle_id`.
- The commander is counted or excluded according to the explicit input setting.
- A known complete Commander Spellbook combo is shown with prerequisites and a source link.
- A near combo is visible but adds no complete-combo points.
- An unresolved card, rate limit, or provider outage returns an incomplete result—never a false zero.
- A price-provider outage does not alter the legality, policy, or power result.

## Ship order

1. Scryfall resolver, cache, Commander legality, and imported-deck error handling.
2. Versioned Game Changers snapshot and a clear count in the deck view.
3. Commander Spellbook complete/near-combo reporting.
4. Transparent power-v1 ruleset with fixtures and an evidence-first UI.
5. Optional CardTrader adapter for exact-printing inventory and cart preparation, behind an owner-controlled credential boundary.

That order produces a useful tool early and keeps the expensive or access-controlled marketplace work from blocking the features players will actually use every day.
