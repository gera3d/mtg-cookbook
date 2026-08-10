# MTG Cookbook edge service

The public pages remain in the `gera3d/mtg-cookbook-site` GitHub Pages repository. This Worker owns only two same-origin endpoints on `mtg.why57.com`:

- `POST /api/store-inquiries` validates Turnstile and stores a short, owner-controlled shop inquiry in D1.
- `POST /api/events` stores a daily count for a small allowlist of conversion events.

It does not store IP addresses, cookies, referrers, page URLs, advertising identifiers, inventory files, or payment information. The inquiry form asks only for the data a shop voluntarily supplies: shop name, work email, locations, current systems, and the visibility problem.

## Owner operations

The `TURNSTILE_SECRET_KEY` is a Cloudflare Worker secret and must be set with Wrangler. It is never committed to this project.

View recent inquiries:

```sh
npx --yes wrangler@latest d1 execute mtg-cookbook-leads --remote --command "SELECT received_at, shop_name, work_email, locations, systems, visibility_problem, message FROM store_inquiries ORDER BY received_at DESC LIMIT 50"
```

View the daily conversion summary:

```sh
npx --yes wrangler@latest d1 execute mtg-cookbook-leads --remote --command "SELECT day, event_name, count FROM daily_events ORDER BY day DESC, event_name ASC"
```

Delete an inquiry only when its business purpose has ended:

```sh
npx --yes wrangler@latest d1 execute mtg-cookbook-leads --remote --command "DELETE FROM store_inquiries WHERE id = '<inquiry-id>'"
```

The event names are intentionally limited to path selection, the store-service CTA, form start, and completed inquiry. `store_inquiry_submitted` is written server-side only after a successful verified form submission.
