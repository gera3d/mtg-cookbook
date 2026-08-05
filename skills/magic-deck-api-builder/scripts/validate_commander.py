#!/usr/bin/env python3
"""Validate Commander deck count and singleton constraints without network access."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path


BASIC_LANDS = {
    "Plains",
    "Island",
    "Swamp",
    "Mountain",
    "Forest",
    "Wastes",
    "Snow-Covered Plains",
    "Snow-Covered Island",
    "Snow-Covered Swamp",
    "Snow-Covered Mountain",
    "Snow-Covered Forest",
}
LINE = re.compile(r"^(?P<quantity>\d+)\s+(?P<name>.+?)\s*$")


def parse_decklist(path: Path) -> Counter[str]:
    cards: Counter[str] = Counter()
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#") or line.lower().startswith("sideboard"):
            continue
        if line.lower().startswith("commander:"):
            line = f"1 {line.split(':', 1)[1].strip()}"
        match = LINE.match(line)
        if not match:
            raise ValueError(f"Line {number} is not '<quantity> <card name>': {raw}")
        cards[match["name"]] += int(match["quantity"])
    return cards


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("decklist", type=Path, help="Text decklist: one '<quantity> <card>' entry per line")
    parser.add_argument("--commander", help="Commander name to require exactly once")
    parser.add_argument("--expected-size", type=int, default=100, help="Deck size to require (default: 100)")
    args = parser.parse_args()

    try:
        cards = parse_decklist(args.decklist)
    except (OSError, ValueError) as exc:
        print(json.dumps({"ok": False, "errors": [str(exc)]}, indent=2))
        return 2

    total = sum(cards.values())
    duplicate_nonbasics = sorted(
        name for name, quantity in cards.items() if quantity > 1 and name not in BASIC_LANDS
    )
    errors: list[str] = []
    if total != args.expected_size:
        errors.append(f"Deck has {total} cards; expected {args.expected_size}.")
    if duplicate_nonbasics:
        errors.append("Nonbasic duplicate(s): " + ", ".join(duplicate_nonbasics))
    if args.commander and cards[args.commander] != 1:
        errors.append(f"Commander '{args.commander}' appears {cards[args.commander]} time(s); expected 1.")

    result = {
        "ok": not errors,
        "total_cards": total,
        "unique_card_names": len(cards),
        "commander": args.commander,
        "duplicate_nonbasics": duplicate_nonbasics,
        "errors": errors,
        "warnings": [
            "This offline check does not verify color identity, format legality, or card-name spelling."
        ],
    }
    print(json.dumps(result, indent=2))
    return 0 if not errors else 2


if __name__ == "__main__":
    sys.exit(main())
