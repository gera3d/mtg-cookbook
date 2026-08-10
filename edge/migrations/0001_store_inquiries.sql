CREATE TABLE IF NOT EXISTS store_inquiries (
  id TEXT PRIMARY KEY,
  received_at TEXT NOT NULL,
  shop_name TEXT NOT NULL,
  work_email TEXT NOT NULL,
  locations TEXT,
  systems TEXT,
  visibility_problem TEXT NOT NULL,
  message TEXT
);

CREATE TABLE IF NOT EXISTS daily_events (
  day TEXT NOT NULL,
  event_name TEXT NOT NULL,
  count INTEGER NOT NULL DEFAULT 0 CHECK (count >= 0),
  PRIMARY KEY (day, event_name)
);
