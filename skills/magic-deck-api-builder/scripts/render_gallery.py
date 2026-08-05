#!/usr/bin/env python3
"""Render a standalone Magic deck gallery from normalized JSON data."""

from __future__ import annotations

import argparse
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def money(value: Any, currency: str) -> str:
    return "owned" if value is None else f"{currency}{float(value):.2f}"


def esc(value: Any) -> str:
    return html.escape(str(value or ""), quote=True)


def flatten(data: dict[str, Any]) -> list[dict[str, Any]]:
    return [card for group in data["groups"] for card in group.get("cards", [])]


def render(data: dict[str, Any]) -> str:
    currency = data.get("price", {}).get("currency", "$")
    cards = flatten(data)
    buy_count = sum(int(card.get("quantity", 1)) for card in cards if not card.get("owned"))
    owned_count = sum(int(card.get("quantity", 1)) for card in cards if card.get("owned"))
    total_count = buy_count + owned_count
    quoted = data.get("price", {}).get("quoted_total")
    score = data.get("strength", {})
    checked_at = data.get("price", {}).get("checked_at", "not yet checked")
    quote_scope = data.get("price", {}).get("scope", "live listing quote")
    note = data.get("price", {}).get("note", "Checkout fees, shipping, tax, and stock can change.")

    sections = []
    for group in data["groups"]:
        rows = []
        for card in group.get("cards", []):
            quantity = int(card.get("quantity", 1))
            label = f"{quantity} {card['name']}" if quantity > 1 else card["name"]
            meta = " · ".join(
                value
                for value in [
                    card.get("role"),
                    card.get("printing"),
                    card.get("language"),
                    card.get("condition"),
                ]
                if value
            )
            rows.append(
                "<button class='card' data-name='{name}' data-meta='{meta}' data-price='{price}'>"
                "<span class='card-name'>{label}</span><span class='card-price {owned}'>{price}</span></button>".format(
                    name=esc(card["name"]),
                    meta=esc(meta),
                    label=esc(label),
                    price=esc(money(None if card.get("owned") else card.get("price"), currency)),
                    owned="owned" if card.get("owned") else "",
                )
            )
        sections.append(
            "<section><h2>{title}<small>{count} cards</small></h2><div class='card-grid'>{rows}</div></section>".format(
                title=esc(group.get("title", "Cards")),
                count=sum(int(card.get("quantity", 1)) for card in group.get("cards", [])),
                rows="".join(rows),
            )
        )

    decklist = "\n".join(
        f"{int(card.get('quantity', 1))} {card['name']}" for card in cards
    )
    payload = json.dumps({"decklist": decklist})
    return f"""<!doctype html>
<html lang='en'>
<head>
<meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>
<title>{esc(data.get('title', 'Magic deck'))}</title>
<style>
:root{{--bg:#100b0b;--panel:#211616;--panel2:#2d1918;--ink:#fff4e8;--muted:#c6b7ae;--line:#634038;--red:#f05d37;--gold:#f5bd62;--green:#a9e5ae;--blue:#a9d9f2}}*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at 86% -8%,#67291d,transparent 31%),var(--bg);color:var(--ink);font:16px/1.5 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}main{{max-width:1260px;margin:auto;padding:34px 22px 48px}}.eyebrow,h2{{color:var(--gold);font-size:.77rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase}}h1{{max-width:900px;margin:8px 0;font-size:clamp(2.25rem,5vw,4.25rem);line-height:1;letter-spacing:-.05em}}.subhead,.muted{{color:var(--muted)}}.pills{{display:flex;gap:8px;flex-wrap:wrap;margin:20px 0}}.pill{{padding:7px 11px;border:1px solid var(--line);border-radius:999px;background:var(--panel);font-size:.88rem}}.pill strong,.price{{color:var(--green)}}.notice,.rating,.ledger{{margin-top:19px;padding:15px 17px;border-radius:10px;background:var(--panel);border:1px solid var(--line)}}.notice{{border-left:3px solid var(--red);color:var(--muted)}}.rating{{display:grid;grid-template-columns:1fr auto;gap:18px;border-color:#9a763c}}.rating p{{margin:4px 0 0;color:var(--muted)}}.score{{display:grid;place-items:center;min-width:105px;border-left:1px solid var(--line);color:var(--gold)}}.score b{{font-size:2.7rem;line-height:1}}.layout{{display:grid;grid-template-columns:minmax(0,1fr) minmax(300px,375px);gap:28px;margin-top:27px}}section{{margin-bottom:24px}}h2{{display:flex;justify-content:space-between;margin:0 0 10px;color:var(--blue)}}h2 small{{color:var(--muted);font-size:.75rem;font-weight:500;letter-spacing:0;text-transform:none}}.card-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(245px,1fr));gap:7px}}.card{{display:flex;justify-content:space-between;gap:9px;overflow:hidden;padding:0;border:1px solid var(--line);border-radius:8px;background:var(--panel);color:var(--ink);cursor:pointer;text-align:left}}.card:hover,.card:focus{{border-color:var(--red);background:var(--panel2);outline:none}}.card-name{{padding:10px 11px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}.card-price{{display:grid;min-width:60px;place-items:center;padding:0 9px;border-left:1px solid var(--line);font-size:.84rem;font-weight:800}}.owned{{color:var(--gold);font-size:.74rem}}.preview{{position:sticky;top:18px;align-self:start;overflow:hidden;border:1px solid var(--line);border-radius:14px;background:var(--panel)}}.art{{display:grid;min-height:420px;place-items:center;background:linear-gradient(135deg,#311617,#682b1c)}}.art img{{display:block;width:100%;height:auto}}.preview-copy{{padding:15px 16px}}.preview-copy h3{{margin:0}}.preview-copy p{{margin:5px 0 0;color:var(--muted);font-size:.88rem}}.copy{{margin-top:17px;padding:8px 11px;border:1px solid var(--line);border-radius:7px;background:var(--panel);color:var(--ink);cursor:pointer}}.ledger dl{{display:grid;grid-template-columns:1fr auto;gap:7px 15px;margin:8px 0 0}}.ledger dt{{color:var(--muted)}}.ledger dd{{margin:0;font-variant-numeric:tabular-nums}}@media(max-width:850px){{main{{padding:25px 16px}}.layout{{grid-template-columns:1fr}}.preview{{position:static;order:-1}}.rating{{grid-template-columns:1fr}}.score{{border-left:0;border-top:1px solid var(--line);padding-top:13px}}}}
</style>
</head>
<body><main>
<header>
<div class='eyebrow'>{esc(data.get('format', 'Magic: The Gathering'))} · {esc(data.get('strategy', 'Deck build'))}</div>
<h1>{esc(data.get('title', 'Magic deck'))}</h1>
<p class='subhead'>{esc(data.get('tagline', 'A card-by-card build with live-price context.'))}</p>
<div class='pills'><span class='pill'><strong>{esc(money(quoted, currency))}</strong> {esc(quote_scope)}</span><span class='pill'><strong>{buy_count}</strong> cards to buy</span><span class='pill'><strong>{owned_count}</strong> supplied</span><span class='pill'><strong>{total_count}</strong> total cards</span></div>
<div class='notice'><strong>Quote reality:</strong> {esc(note)} Checked: {esc(checked_at)}.</div>
<div class='rating'><div><h2>Deck strength · {esc(score.get('score', 'unrated'))} / 10</h2><p>{esc(score.get('summary', 'Add a strengths-and-limitations rationale.'))}</p></div><div class='score'><b>{esc(score.get('score', '—'))}</b><span>{esc(score.get('label', 'Unrated'))}</span></div></div>
</header>
<div class='layout'><div><button class='copy' id='copy' type='button'>Copy exact decklist</button>{''.join(sections)}</div>
<aside class='preview' aria-live='polite'><div class='art' id='art'><span class='muted'>Hover a card to load its art.</span></div><div class='preview-copy'><h3 id='preview-name'>{esc(data.get('commander', 'Deck preview'))}</h3><p id='preview-meta'>Card art and rules text come from Scryfall.</p><p id='preview-rules'></p></div></aside></div>
<section class='ledger'><strong>Cost ledger</strong><dl><dt>Quoted cards</dt><dd class='price'>{esc(money(quoted, currency))}</dd><dt>Cards supplied by owner</dt><dd>{owned_count}</dd><dt>Checkout fees, shipping, and tax</dt><dd>not assumed</dd></dl></section>
</main>
<script>const data={payload};const art=document.querySelector('#art'),name=document.querySelector('#preview-name'),meta=document.querySelector('#preview-meta'),rules=document.querySelector('#preview-rules'),cache=new Map();async function preview(button){{const card=button.dataset.name;name.textContent=card;meta.textContent=[button.dataset.price,button.dataset.meta].filter(Boolean).join(' · ');rules.textContent='Loading card image and rules…';try{{let d=cache.get(card);if(!d){{const r=await fetch('https://api.scryfall.com/cards/named?exact='+encodeURIComponent(card));if(!r.ok)throw Error();d=await r.json();cache.set(card,d)}}const image=d.image_uris?.normal||d.card_faces?.[0]?.image_uris?.normal;if(!image)throw Error();art.innerHTML='<img src="'+image+'" alt="'+d.name.replace(/"/g,'&quot;')+'">';rules.textContent=[d.type_line,d.oracle_text].filter(Boolean).join(' · ')}}catch{{art.innerHTML='<span class="muted">Card image unavailable.</span>';rules.textContent='Scryfall could not return this card right now.'}}}}document.querySelectorAll('.card').forEach(button=>{{for(const event of ['mouseenter','focus','click'])button.addEventListener(event,()=>preview(button))}});document.querySelector('#copy').addEventListener('click',async()=>{{try{{await navigator.clipboard.writeText(data.decklist);document.querySelector('#copy').textContent='Decklist copied'}}catch{{document.querySelector('#copy').textContent='Copy unavailable'}}}});</script>
</body></html>"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", type=Path, help="Normalized deck JSON")
    parser.add_argument("--out", type=Path, help="Output HTML file")
    args = parser.parse_args()
    data = json.loads(args.data.read_text(encoding="utf-8"))
    if not data.get("groups"):
        raise SystemExit("deck data must contain at least one group")
    output = args.out or args.data.with_suffix(".html")
    output.write_text(render(data), encoding="utf-8")
    print(json.dumps({"output": str(output), "generated_at": datetime.now(timezone.utc).isoformat()}))


if __name__ == "__main__":
    main()
