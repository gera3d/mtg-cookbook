# MTG Cookbook

Practical, installable Skills for building Magic: The Gathering decks with real rules data, live marketplace quotes, and a clear purchase boundary.

The point is not to generate a pile of card names. The point is to get to a deck you can actually play, understand, price, and buy without quietly compromising the constraints you gave it.

## Start here

### Magic Deck API Builder

[`magic-deck-api-builder`](skills/magic-deck-api-builder/) is the first public Skill in this cookbook. It helps an agent or harness:

- Turn a Commander brief into an exact 100-card decklist.
- Validate Commander count and singleton rules with a deterministic local check.
- Separate card-data truth from live marketplace inventory and checkout totals.
- Enforce hard buying constraints such as **English only**, card condition, foil treatment, service, and budget.
- Render a standalone deck gallery with hover card art, rules text, quoted per-card prices, and a practical power assessment.
- Prepare a cart but pause for a fresh confirmation immediately before a payment is submitted.

The Skill includes a Commander validator, a gallery generator, example input data, and guidance for connecting card-data and marketplace adapters without publishing secrets.

## Install

The portable unit is the [`SKILL.md`](skills/magic-deck-api-builder/SKILL.md) folder and its supporting files. `agents/openai.yaml` is optional appearance and dependency metadata for the ChatGPT/Codex experience; it is not a required adapter.

Clone the repository from the project where you want to use the Skill:

```bash
git clone https://github.com/gera3d/mtg-cookbook.git
```

Then copy the same folder to the path your harness reads:

| Harness | Project install | Personal install |
| --- | --- | --- |
| Claude Code | `mkdir -p .claude/skills && cp -R mtg-cookbook/skills/magic-deck-api-builder .claude/skills/` | `mkdir -p ~/.claude/skills && cp -R mtg-cookbook/skills/magic-deck-api-builder ~/.claude/skills/` |
| Codex | `mkdir -p .agents/skills && cp -R mtg-cookbook/skills/magic-deck-api-builder .agents/skills/` | `mkdir -p ~/.agents/skills && cp -R mtg-cookbook/skills/magic-deck-api-builder ~/.agents/skills/` |

Claude Code project Skills live in `.claude/skills/`; Codex project Skills live in `.agents/skills/`. Each personal path makes the Skill available across that person's projects. You can invoke Claude Code with `/magic-deck-api-builder` and Codex with `$magic-deck-api-builder`, or let either one select the Skill when the task matches its description.

Read the current host documentation before changing how your setup discovers Skills: [Claude Code Skills](https://code.claude.com/docs/en/skills) and [OpenAI's Codex Skills guide](https://learn.chatgpt.com/docs/build-skills).

## What a good deck request looks like

> Build a budget Commander deck around this commander. I already own the commander and basic lands. Keep listings English only and in at least lightly played condition. Use CardTrader Zero if possible, cap the cards at $35 before checkout fees, and show me a gallery plus the exact checkout quote before touching a cart.

That brief gives the workflow something it can enforce. "Cheapest" alone is not enough: it can otherwise mean non-English cards, bad condition, a different printing, or a price that excludes service fees and shipping.

## Recipe library

- [Build a budget Commander deck](recipes/build-a-budget-commander-deck.md) — from deck brief through legal-list validation, quote review, and a final owner gate.
- [Commander intelligence](skills/magic-deck-api-builder/references/commander-intelligence.md) — public data sources, Game Changers policy sync, combo detection, and an explainable power estimate.
- [Commander deck intelligence build spec](specs/commander-deck-intelligence.md) — feature backlog, API boundaries, acceptance criteria, and owner gates for the app.

## Ground rules

- **Rules and prices are different sources of truth.** Validate card facts and legality against live card data; quote availability and cost from live marketplace inventory.
- **A price scan is not checkout.** Keep article subtotal, service fees, shipping, tax, and final total separate.
- **Language and condition are real constraints.** English-only is a hard filter, not a preference to waive when inventory is thin.
- **No secrets in the cookbook.** API credentials, cookies, addresses, and payment details stay in named harness integrations.
- **No automatic charge.** The user sees a fresh, exact final total and explicitly confirms before payment.

## Project layout

```text
skills/
  magic-deck-api-builder/       # Installable portable Skill
recipes/
  build-a-budget-commander-deck.md
```

## Contributing

Add a Skill or recipe only when it leaves someone with a useful decision or a repeatable workflow. Include the actual files, truthful source boundaries, and the owner gate for any external action. Don't publish private marketplace, order, address, or payment data.
