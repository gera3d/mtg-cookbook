const SITE_ORIGIN = "https://mtg.why57.com";
const GITHUB_PAGES_ORIGIN = "https://gera3d.github.io";
const GITHUB_PAGES_BASE_PATH = "/mtg-cookbook-site";
const MAX_JSON_BYTES = 12_000;

const eventNames = new Set([
  "path_overview_viewed",
  "path_store_viewed",
  "path_research_viewed",
  "path_skills_viewed",
  "deck_detail_viewed",
  "cta_store_service_clicked",
  "store_inquiry_started"
]);

type StoreInquiry = {
  shopName: string;
  email: string;
  locations: string;
  systems: string;
  visibilityProblem: string;
  message: string;
  website: string;
  turnstileToken: string;
};

const responseHeaders = {
  "Cache-Control": "no-store",
  "Content-Type": "application/json; charset=utf-8",
  "X-Content-Type-Options": "nosniff"
};

function json(body: Record<string, unknown>, status = 200): Response {
  return new Response(JSON.stringify(body), { status, headers: responseHeaders });
}

function methodNotAllowed(): Response {
  return new Response(JSON.stringify({ ok: false, message: "Method not allowed." }), {
    status: 405,
    headers: { ...responseHeaders, Allow: "POST" }
  });
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

async function readJson(request: Request): Promise<Record<string, unknown> | null> {
  const declaredLength = Number(request.headers.get("Content-Length"));
  if (Number.isFinite(declaredLength) && declaredLength > MAX_JSON_BYTES) return null;

  const reader = request.body?.getReader();
  if (!reader) return null;

  const chunks: Uint8Array[] = [];
  let totalBytes = 0;
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      totalBytes += value.byteLength;
      if (totalBytes > MAX_JSON_BYTES) return null;
      chunks.push(value);
    }
  } finally {
    reader.releaseLock();
  }

  const body = new Uint8Array(totalBytes);
  let offset = 0;
  for (const chunk of chunks) {
    body.set(chunk, offset);
    offset += chunk.byteLength;
  }

  try {
    const parsed: unknown = JSON.parse(new TextDecoder().decode(body));
    return isRecord(parsed) ? parsed : null;
  } catch {
    return null;
  }
}

function text(value: unknown, maxLength: number, required = false): string | null {
  if (typeof value !== "string") return required ? null : "";
  const normalized = value.trim();
  if ((required && !normalized) || normalized.length > maxLength) return null;
  return normalized;
}

function readStoreInquiry(input: Record<string, unknown>): StoreInquiry | null {
  const shopName = text(input.shopName, 160, true);
  const email = text(input.email, 254, true);
  const locations = text(input.locations, 320);
  const systems = text(input.systems, 500);
  const visibilityProblem = text(input.visibilityProblem, 1_500, true);
  const message = text(input.message, 2_000);
  const website = text(input.website, 200);
  const turnstileToken = text(input.turnstileToken, 2_048, true);

  if (
    shopName === null ||
    email === null ||
    locations === null ||
    systems === null ||
    visibilityProblem === null ||
    message === null ||
    website === null ||
    turnstileToken === null ||
    !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
  ) {
    return null;
  }

  return { shopName, email, locations, systems, visibilityProblem, message, website, turnstileToken };
}

function hasExpectedOrigin(request: Request): boolean {
  return request.headers.get("Origin") === SITE_ORIGIN;
}

function dayStamp(): string {
  return new Date().toISOString().slice(0, 10);
}

async function incrementEvent(env: Env, eventName: string): Promise<void> {
  await env.LEADS
    .prepare(
      "INSERT INTO daily_events (day, event_name, count) VALUES (?1, ?2, 1) " +
        "ON CONFLICT(day, event_name) DO UPDATE SET count = count + 1"
    )
    .bind(dayStamp(), eventName)
    .run();
}

async function validateTurnstile(env: Env, token: string): Promise<boolean> {
  const form = new FormData();
  form.set("secret", env.TURNSTILE_SECRET_KEY);
  form.set("response", token);
  form.set("idempotency_key", crypto.randomUUID());

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 10_000);
  try {
    const response = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
      method: "POST",
      body: form,
      signal: controller.signal
    });
    if (!response.ok) return false;
    const result: unknown = await response.json();
    return (
      isRecord(result) &&
      result.success === true &&
      result.hostname === "mtg.why57.com" &&
      result.action === "store-inquiry"
    );
  } catch {
    return false;
  } finally {
    clearTimeout(timeout);
  }
}

async function handleEvent(request: Request, env: Env): Promise<Response> {
  if (request.method !== "POST") return methodNotAllowed();
  if (!hasExpectedOrigin(request)) return json({ ok: false, message: "Origin not allowed." }, 403);
  if (!request.headers.get("Content-Type")?.includes("application/json")) {
    return json({ ok: false, message: "JSON is required." }, 415);
  }

  const input = await readJson(request);
  const eventName = input && text(input.eventName, 80, true);
  if (!eventName || !eventNames.has(eventName)) {
    return json({ ok: false, message: "Event not allowed." }, 400);
  }

  try {
    await incrementEvent(env, eventName);
    return json({ ok: true }, 202);
  } catch {
    console.error(JSON.stringify({ event: "measurement-write-failed" }));
    return json({ ok: false, message: "Unable to record event." }, 503);
  }
}

async function handleStoreInquiry(request: Request, env: Env): Promise<Response> {
  if (request.method !== "POST") return methodNotAllowed();
  if (!hasExpectedOrigin(request)) return json({ ok: false, message: "Origin not allowed." }, 403);
  if (!request.headers.get("Content-Type")?.includes("application/json")) {
    return json({ ok: false, message: "JSON is required." }, 415);
  }

  const input = await readJson(request);
  if (!input) return json({ ok: false, message: "Please review the form and try again." }, 400);
  const inquiry = readStoreInquiry(input);
  if (!inquiry || inquiry.website) return json({ ok: false, message: "Please review the form and try again." }, 400);

  const verified = await validateTurnstile(env, inquiry.turnstileToken);
  if (!verified) {
    console.warn(JSON.stringify({ event: "store-inquiry-rejected", reason: "turnstile" }));
    return json({ ok: false, message: "Verification expired or could not be confirmed. Please try again." }, 400);
  }

  const id = crypto.randomUUID();
  const receivedAt = new Date().toISOString();
  try {
    await env.LEADS.batch([
      env.LEADS
        .prepare(
          "INSERT INTO store_inquiries (id, received_at, shop_name, work_email, locations, systems, visibility_problem, message) " +
            "VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8)"
        )
        .bind(
          id,
          receivedAt,
          inquiry.shopName,
          inquiry.email,
          inquiry.locations || null,
          inquiry.systems || null,
          inquiry.visibilityProblem,
          inquiry.message || null
        ),
      env.LEADS
        .prepare(
          "INSERT INTO daily_events (day, event_name, count) VALUES (?1, ?2, 1) " +
            "ON CONFLICT(day, event_name) DO UPDATE SET count = count + 1"
        )
        .bind(dayStamp(), "store_inquiry_submitted")
    ]);
    return json({ ok: true, message: "Your inquiry was recorded. We will respond within two business days if there is a practical next step." }, 201);
  } catch {
    console.error(JSON.stringify({ event: "store-inquiry-write-failed" }));
    return json({ ok: false, message: "We could not save your inquiry. Please email gera3d@gmail.com instead." }, 503);
  }
}

async function proxyStaticSite(request: Request): Promise<Response> {
  const incoming = new URL(request.url);
  const upstream = new URL(`${GITHUB_PAGES_BASE_PATH}${incoming.pathname}`, GITHUB_PAGES_ORIGIN);
  upstream.search = incoming.search;

  const response = await fetch(new Request(upstream, request));
  const headers = new Headers(response.headers);
  headers.set("X-MTG-Origin", "github-pages");
  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers
  });
}

export default {
  async fetch(request, env): Promise<Response> {
    const pathname = new URL(request.url).pathname;
    if (pathname === "/api/events") return handleEvent(request, env);
    if (pathname === "/api/store-inquiries") return handleStoreInquiry(request, env);
    return proxyStaticSite(request);
  }
} satisfies ExportedHandler<Env>;
