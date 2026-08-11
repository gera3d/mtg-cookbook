# Commander Deck Intelligence — Build Spec

## Outcome

Build a deck decision engine, not another card-search page. A player pastes a Commander decklist and gets a source-backed answer to five practical questions:

1. Is this deck legal?
2. How many Game Changers are in it?
3. Which known combos are complete or nearly complete?
4. What power band is it likely to play in, and why?
5. What should the player change, use from their collection, or buy next?

The app must show uncertainty honestly. An unresolved card, stale price, unavailable listing, or unavailable provider is **unknown**, not zero and not a reason to invent an answer.

The provider boundaries, access rules, and data-handling requirements live in [Commander intelligence](../skills/magic-deck-api-builder/references/commander-intelligence.md). This document specifies the features to build.

## Product constraints

- **Facts before prose.** Rules, identities, policy matches, prices, and score arithmetic are deterministic and source-backed. An LLM may explain the result; it must not invent it.
- **Exact printing is distinct from gameplay identity.** Use `oracle_id` for rules-level matches and Scryfall printing ID, set, collector number, language, and finish for a real marketplace listing.
- **A power score is an estimate, not an official ruling.** It starts a pregame conversation; it does not certify a Commander bracket or guaranteed win turn.
- **Marketplace actions are owner-gated.** Research and quote preparation are safe. Cart mutation, accepting substitutions, and payment require explicit user approval at the time of action.
- **No secret in the client.** CardTrader tokens and webhook secrets stay in a server-side named credential action.

## mtg.why57.com delivery architecture

### Product decision

Deliver the first version as a **Deck Lab** on `mtg.why57.com`: a deck library with saved, source-backed insight for every owned Commander deck.

Do not turn every visitor page load into a live analysis job. The site is a static GitHub Pages site proxied through a Cloudflare Worker, so the correct first implementation is a build-time analysis pipeline that publishes small JSON reports beside the static site.

```text
deck source
  -> normalized deck manifest
  -> Scryfall resolver + controlled cache
  -> legality + Game Changers policy match + role classification
  -> Commander Spellbook combo lookup
  -> versioned report JSON + compact library index
  -> static Deck Lab UI on mtg.why57.com
```

The public browser reads a generated report and its `analyzed_at` timestamp. It does not call Scryfall or Commander Spellbook for every hover, filter, or deck page load.

### Existing-site boundary

- Keep `my-decks.html` as the historical CardTrader research archive. Do not mix historic price research with gameplay intelligence.
- Promote the existing local collection-gallery approach into a dedicated, released `decks.html` Deck Lab route instead of overwriting the research archive.
- Add the Deck Lab page, its compact index JSON, per-deck analysis JSON, and necessary shared assets to the explicit release-file allowlist. The local gallery and collection-data files are currently outside that release surface.
- Keep the first release public but `noindex` unless the owner instead explicitly chooses private access. Private access requires an authentication design before release.
- Keep CardTrader purchase, cart, seller, and pricing concerns outside the P0 analysis pipeline.

### Deck manifest

Replace the one-string commander field with a normalized source manifest. A deck must support one or more commanders.

```json
{
  "id": "frodo-sam-food-and-fellowship",
  "name": "Food and Fellowship",
  "commanders": ["Frodo, Adventurous Hobbit", "Sam, Loyal Attendant"],
  "cards": [
    {
      "input_name": "Sol Ring",
      "quantity": 1,
      "set": null,
      "collector_number": null,
      "finish": null
    }
  ],
  "role_overrides": {},
  "visibility": "public_noindex"
}
```

The analysis process may add resolved `oracle_id` and `scryfall_id` values, but the source deck manifest preserves the original input line and any exact-printing information.

### Generated data contract

Generate two static assets:

- `data/deck-intelligence/index.json`: one compact row per deck for the Deck Lab library.
- `data/deck-intelligence/<deck-id>.json`: the full reproducible report, including sources, policy version, timestamps, blockers, Game Changers, combos, role evidence, and score limitations.

A report status must be one of `complete`, `needs_attention`, `incomplete`, or `stale`. A provider error, unresolved card, or policy mismatch is never represented as a zero.

### Deck Lab user experience

The library card for each deck shows:

- commander or commander pair;
- deck name and card count;
- analysis status and checked date;
- Game Changers count;
- complete-combo count;
- Commander Spellbook bracket signal.

Selecting a deck opens an insight view in this order:

1. **Blockers and fixes** — legality problems, unresolved inputs, and missing commander metadata.
2. **Game Changers** — named cards, commander/mainboard treatment, policy source, and snapshot date.
3. **Complete combos before near combos** — outcome, prerequisites, and source permalink.
4. **Deck health** — lands, ramp, draw, interaction, protection, curve, and role-classification limits.
5. **Power and pod-fit explanation** — versioned, evidence-backed, and explicitly an estimate.
6. **Best next action** — a concrete fix, swap candidate, owned-card option, or later buy-plan handoff.

Show the numeric power score only when its ruleset version and confidence are present. Until calibration is accepted, label it as an experimental signal rather than a public deck-power verdict.

### Refresh and change model

P0 refreshes analyses only through the owner build workflow: deck data change, reviewed policy update, or intentional refresh. Add caching, rate limiting, meaningful request headers, and source timestamps to the build adapters.

Do not add a public “refresh this deck” button in P0. A later owner-only comparison endpoint can support hypothetical adds/removes through a Cloudflare Worker, with controlled cache and no marketplace authority.

### Tested baseline: August 11, 2026

The local pilot completed 13 deck analyses using Scryfall, Commander Spellbook, and the reviewed February 9, 2026 Game Changers policy snapshot.

- 11 decks were legal.
- `Aerith, Last Ancient` needs a commander/list correction: a white-green commander has red cards in the list.
- `Sephiroth, Fabled SOLDIER` needs one duplicate removed: two `Sidisi, Undead Vizier` entries.
- `Frodo, Adventurous Hobbit` becomes legal when `Sam, Loyal Attendant` is represented as a co-commander. This validates the commanders-array requirement.
- `Yuna, Grand Summoner` contains `Farewell`, one complete Commander Spellbook combo, and 35 near combos.
- `Iron Man, Titan of Innovation` contains four Game Changers.

The pilot also exposed and corrected transform-card resolution, basic-land printing-label normalization, paired-commander handling, and an early role-classification error that counted lands as ramp. Keep those as regression fixtures.

### Delivery sequence

1. Normalize deck manifests and repair the two tested deck-data blockers.
2. Make the analysis generator deterministic, cache-aware, and fixture-tested.
3. Generate and review reports for every deck.
4. Release the `decks.html` Deck Lab with a compact library index and per-deck insight view.
5. Calibrate the public-facing power treatment from reviewed role rules and the tested reports.
6. Add a reversible change sandbox.
7. Add owned-card recommendations.
8. Add protected exact-printing buy planning only after the analysis layer is trusted.

## Build order

| Priority | Feature | Why it comes now |
| --- | --- | --- |
| P0 | F01 Deck intake and resolver | Every later feature needs card identity certainty. |
| P0 | F02 Commander legality inspector | A useful deck tool cannot hide invalid lists. |
| P0 | F03 Game Changers scanner | Direct, explainable answer to a real Commander question. |
| P0 | F04 Combo Radar | Turns card data into actual win-line insight. |
| P0 | F05 Explainable power estimate | Makes the tool useful for pod-fit decisions. |
| P0 | F06 Deck health audit and change sandbox | Converts analysis into clear action. |
| P1 | F07 Collection-aware upgrades | Prioritizes cards the player already owns. |
| P1 | F08 Exact-printing buy planner | Converts an approved upgrade path into a truthful quote. |
| P2 | F09 Seller control panel | Valuable operations work, but independent from player deck intelligence. |

Do not hold up P0 for CardTrader, TCGplayer, or Cardmarket marketplace access.

## User experience

```text
Paste/import decklist
  -> resolve cards and correct any ambiguous entries
  -> run legality, Game Changers, combo, and deck-health analysis
  -> explain the power estimate and strongest weaknesses
  -> test a proposed change
  -> optionally use owned cards or request an exact-printing buy plan
```

The main result screen should answer the decision in this order:

1. **Blockers** — invalid commander, duplicate, off-color card, unresolved line.
2. **Game Changers** — count, names, official-policy version.
3. **Known combos** — complete before near-complete.
4. **Power and pod fit** — score plus its evidence and limitations.
5. **Best next action** — fix, swap, use an owned card, or create a buy plan.

## Feature backlog

### F01 — Deck intake and identity resolver

**Player job:** “Turn this list into the exact cards I mean.”

**Uses:** Scryfall API. MTGJSON is an optional local/offline index, not the real-time source of truth.

**Inputs:** Plain-text decklist, common exported decklist formats, optional commander, and optional set/collector/finish data.

**Behavior:**

- Parse quantity, card name, optional set code, collector number, and finish.
- Preserve each original input line for helpful errors.
- Resolve the card to both a printing-specific Scryfall ID and an `oracle_id`.
- Mark an entry as resolved, ambiguous, unresolved, or malformed.
- Require the player to resolve ambiguity before claiming a complete analysis.

**Result contract:**

```json
{
  "resolution": {
    "resolved_count": 98,
    "ambiguous": [{ "input": "Lightning Bolt", "candidates": ["..."] }],
    "unresolved": [{ "input": "Sol Ring (proxy)", "reason": "Unrecognized suffix" }],
    "fetched_at": "2026-08-10T00:00:00Z"
  }
}
```

**Acceptance criteria:**

- A reprint resolves to the same gameplay identity but retains its distinct printing data.
- The UI never silently substitutes a printing or a similarly named card.
- A deck with any unresolved lines is labelled **analysis incomplete**.

---

### F02 — Commander legality inspector

**Player job:** “Can I play this deck as submitted?”

**Uses:** Scryfall card identities, color identity, type lines, and Commander legality.

**Behavior:**

- Verify exactly 100 cards, including the commander.
- Detect prohibited duplicates while respecting card-specific exceptions.
- Check every card against the commander’s color identity.
- Flag Commander-banned and otherwise ineligible cards.
- Show land count and unresolved cards as structural warnings, separate from legality failures.

**Result example:**

```text
Legal Commander deck: No

• 101 cards total
• Counterspell is outside the commander's color identity
• Sol Ring appears twice
```

**Acceptance criteria:** Every failure names the relevant card, rule, and practical next move. A price-provider failure must not affect legality.

---

### F03 — Official Game Changers scanner

**Player job:** “How many Game Changers are in this deck?”

**Uses:** A reviewed, versioned snapshot of Wizards’ official Game Changers policy, matched through Scryfall `oracle_id`.

**Behavior:**

- Match reprints by `oracle_id`, not display name.
- Report distinct cards, copies, names, zones, and whether the commander is included.
- Show the policy source URL, source date, and local snapshot version.
- Support policy versions so historic analyses can be reproduced.

**Result example:**

```text
Game Changers: 3

• Rhystic Study
• Ancient Tomb
• Demonic Tutor

Policy checked: Commander update dated 2026-02-09
```

**Acceptance criteria:** A card that appears in multiple printings is counted once in `distinct_cards`; an official list update becomes a reviewed new snapshot, never a silent overwrite.

---

### F04 — Combo Radar

**Player job:** “Which win lines are already in this deck?”

**Uses:** Commander Spellbook, after the deck is resolved.

**Behavior:**

- Find documented complete combos and near combos.
- Preserve the provider’s combo ID, permalink, prerequisites, required cards, and stated result.
- Classify each line as complete, near, illegal/color-incompatible, or unknown.
- Show prerequisites such as mana, haste, graveyard state, or board setup.

**Result example:**

```text
1 complete combo
• Thassa's Oracle + Demonic Consultation
  Result: Win the game
  Requirement: Resolve Oracle, then Consultation

2 near combos
• Missing one card: ...
```

**Acceptance criteria:** Near combos are visible but add no complete-combo score. Provider failure is reported as unknown; it never becomes “no combos found.”

---

### F05 — Explainable power and pod-fit estimate

**Player job:** “What kind of table is this deck actually suited for?”

**Uses:** Scryfall rules data, F03 Game Changers results, F04 documented combo evidence, and a versioned internal classification ruleset.

**Scoring model:**

| Signal | Range | Examples of evidence |
| --- | ---: | --- |
| Acceleration | 0–20 | Fast mana, early ramp, color access |
| Consistency | 0–20 | Tutors, selection, repeatable draw |
| Win pressure | 0–25 | Complete compact combos, credible finishers |
| Interaction | 0–15 | Efficient answers and protection |
| Mana efficiency | 0–10 | Curve, lands, fixing, dead-card risk |
| Resilience | 0–10 | Redundancy, recursion, recovery |

**Rules:**

- Maintain a versioned role-classification ruleset; do not ask an LLM to guess silently from card art or names.
- Do not double-count a Game Changer as bonus points solely for appearing on the policy list. It should appear as a high-signal explanation and contribute only through the relevant category, such as acceleration or consistency.
- Report a 0–100 internal score and an optional rounded 0–10 display score.
- Report confidence and known limitations.

**Result contract:**

```json
{
  "power": {
    "ruleset_version": "power-v1",
    "score_100": 74,
    "display_score_10": 7.4,
    "pod_fit": "high-power casual",
    "confidence": "medium",
    "signals": [
      { "kind": "fast_mana", "count": 4, "points": 10, "cards": ["..."] },
      { "kind": "complete_combo", "count": 1, "points": 14, "source": "Commander Spellbook" },
      { "kind": "game_changer", "count": 2, "points": 0, "note": "Policy signal" }
    ],
    "limitations": ["Four cards could not be classified"]
  }
}
```

**Acceptance criteria:** The UI explains every material score signal, names the assumed pod fit, and clearly says that the result is an estimate—not an official bracket assignment.

---

### F06 — Deck health audit and change sandbox

**Player job:** “What is this deck missing, and what happens if I change it?”

**Uses:** Scryfall card facts and the F05 ruleset.

**Behavior:**

- Classify cards into lands, ramp, draw, interaction, protection, synergy, and finishers.
- Identify gaps against the commander’s actual strategy, not a generic deck template.
- Let the player simulate an add/remove swap without mutating the saved deck.
- Recalculate legality, Game Changers, combos, curve, role mix, and score delta.

**Result example:**

```text
Add: Mana Vault
Remove: Cultivate

Impact:
• Game Changers: 3 -> 4
• Acceleration: +5
• Estimated power: 7.4 -> 7.9
• Pod fit: likely moves toward a more competitive table
```

**Acceptance criteria:** A proposed change is reversible, the before/after view is clear, and the app explains the tradeoff rather than presenting a number alone.

## Collection and commerce

### F07 — Collection-aware upgrade finder

**Player job:** “Which strong upgrades do I already own?”

**Uses:** The player’s internal collection data plus Scryfall and MTGJSON identifiers.

**Behavior:**

- Match owned printings to legal, relevant upgrade candidates.
- Label each recommendation as already owned, needs purchase, or not legal in the current deck.
- Rank upgrades against the player’s target power and strategy.

**Acceptance criteria:** Owned cards are shown before purchase suggestions. Exact printing is preserved for inventory and display.

---

### F08 — Exact-printing buy planner

**Player job:** “What do I need to buy, and what will it actually cost?”

**Uses:** An authorized, server-side CardTrader adapter. Scryfall is used only for identity, rules, and art reference.

**Behavior:**

- Start with an approved upgrade list, not broad card discovery.
- Apply English, minimum condition, finish, region, and CardTrader Zero constraints before sorting results.
- Normalize every candidate by exact printing, language, condition, finish, seller/service, item price, and quote time.
- Separate article subtotal, marketplace fees, shipping, tax, and final checkout total.
- Prepare a cart only after the user explicitly asks; pause before any payment or substitute acceptance.

**Result example:**

```text
Cards: $18.42
Known fees: $2.10
Shipping: not yet quoted
Final charge: unknown until checkout review
```

**Acceptance criteria:** The UI never labels a card subtotal as a final price and never silently creates a cart, accepts a substitution, or places an order.

---

### F09 — Seller control panel

**Player job:** “Keep my inventory accurate and avoid selling the same card twice.”

**Uses:** CardTrader Full API and verified webhooks through a server-side credential boundary.

**Behavior:**

- Show inventory, orders, synchronization health, and exceptions.
- Track exact product identity: printing, language, condition, finish, quantity, and channel state.
- Receive signed order notifications and preserve an audit trail for every stock change.
- Flag one-of-one conflicts, failed syncs, and orders that require manual handling.

**Acceptance criteria:** The app can explain each inventory adjustment, treats order reversals as first-class events, and never exposes tokens or webhook secrets to the browser.

## Public API and provider rules

| Provider | Role in this build | Decision |
| --- | --- | --- |
| Scryfall | Card facts, rules text, identities, legalities, images | Core dependency; cache and throttle server-side |
| Commander Spellbook | Documented combo evidence | Core dependency after card resolution |
| MTGJSON | Offline data, identifiers, historical snapshots | Supporting dependency; not live checkout truth |
| Wizards Commander updates | Game Changers policy | Manually reviewed/versioned policy snapshots |
| CardTrader Full API | Authorized inventory, orders, and exact-printing marketplace operations | Optional commerce and seller dependency |
| TCGplayer | Potential approved partnership integration | Do not make v1 dependent on it |
| Cardmarket | Restricted provider access | Do not make v1 dependent on it |

## Minimal server contract

```text
POST /api/commander/analyze
  input: commander, mainboard, optional sideboard, policy_version
  output: resolution, legality, game_changers, combos, role_counts,
          power, sources, timestamps, limitations

POST /api/commander/compare
  input: baseline deck, proposed add/remove changes
  output: before/after analysis and explained delta

POST /api/collection/recommendations
  input: deck, collection, target_power
  output: owned upgrades, possible purchases, reasoning

POST /api/buy-plan/quote
  input: approved purchase list and buyer constraints
  output: normalized quotes and incomplete/final-cost status
```

The front end must render partial data honestly. If 98 of 100 cards resolve, show the two unresolved lines and label every dependent result incomplete.

## Quality gates before launch

- A deck with no Game Changers reports zero against a named policy snapshot.
- Reprints match the same Game Changer through `oracle_id`.
- Commander treatment in the Game Changers count is explicit and tested.
- A complete Commander Spellbook combo shows its prerequisites and source link.
- A near combo does not receive complete-combo points.
- A Scryfall rate limit, resolver error, or Combo Radar outage returns incomplete—not false zero.
- Price-provider errors do not change legality, Game Changers, combos, or power.
- Exact-printing quotes never substitute a marketplace or printing silently.
- Cart, substitution, inventory mutation, and payment all require the appropriate owner gate.

## Explicit non-goals for the first release

- Generic price-drop alerts with no decision context.
- Automatic checkout or purchase.
- TCGplayer or Cardmarket dependencies without granted access.
- An opaque “AI knows your power level” score.
- Image card scanning before list resolution and deck intelligence work reliably.

## Definition of useful

The first release is successful when a Commander player can paste a deck, understand its actual strength and table fit, identify any high-impact cards or known combos, and make one better next decision without needing to search five different sites.
