PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS pool_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pool_id TEXT NOT NULL, observed_at TEXT NOT NULL, fetched_at TEXT NOT NULL,
    chain_id TEXT NOT NULL, chain_name TEXT NOT NULL, protocol TEXT NOT NULL,
    version TEXT NOT NULL, pool_address TEXT NOT NULL,
    token0_address TEXT NOT NULL, token0_symbol TEXT NOT NULL,
    token1_address TEXT NOT NULL, token1_symbol TEXT NOT NULL,
    tvl_usd REAL, volume_24h_usd REAL, fees_24h_usd REAL,
    fee_apr_pct REAL, incentive_apr_pct REAL, spot_price REAL,
    current_tick INTEGER, fee_tier_bps REAL,
    source TEXT NOT NULL, source_url TEXT NOT NULL,
    data_status TEXT NOT NULL, raw_ref TEXT
);
CREATE INDEX IF NOT EXISTS idx_pool_snapshots_pool_time ON pool_snapshots(pool_id, observed_at DESC);

CREATE TABLE IF NOT EXISTS position_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    position_id TEXT NOT NULL, wallet_address TEXT NOT NULL,
    observed_at TEXT NOT NULL, fetched_at TEXT NOT NULL,
    chain_id TEXT NOT NULL, protocol TEXT NOT NULL, version TEXT NOT NULL,
    pool_id TEXT NOT NULL, liquidity_raw TEXT,
    tick_lower INTEGER, tick_upper INTEGER, current_tick INTEGER,
    principal_usd REAL, unclaimed_fees_usd REAL, claimed_fees_usd REAL,
    in_range INTEGER, source TEXT NOT NULL, source_url TEXT NOT NULL,
    data_status TEXT NOT NULL, raw_ref TEXT
);
CREATE INDEX IF NOT EXISTS idx_position_wallet_time ON position_snapshots(wallet_address, observed_at DESC);
CREATE INDEX IF NOT EXISTS idx_position_id_time ON position_snapshots(position_id, observed_at DESC);

CREATE TABLE IF NOT EXISTS position_fee_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    position_id TEXT NOT NULL, token_id TEXT NOT NULL, wallet_address TEXT NOT NULL,
    block_number INTEGER NOT NULL, block_hash TEXT NOT NULL, block_timestamp TEXT NOT NULL,
    pool_address TEXT NOT NULL, token0_address TEXT NOT NULL, token1_address TEXT NOT NULL,
    token0_symbol TEXT NOT NULL, token1_symbol TEXT NOT NULL,
    token0_decimals INTEGER NOT NULL, token1_decimals INTEGER NOT NULL,
    tokens_owed0_raw TEXT NOT NULL, tokens_owed1_raw TEXT NOT NULL,
    tokens_owed0_human TEXT NOT NULL, tokens_owed1_human TEXT NOT NULL,
    current_tick INTEGER NOT NULL, tick_lower INTEGER NOT NULL, tick_upper INTEGER NOT NULL,
    liquidity_raw TEXT NOT NULL, fee_tier INTEGER NOT NULL,
    data_status TEXT NOT NULL, raw_ref TEXT
);
CREATE INDEX IF NOT EXISTS idx_position_fee_id_time ON position_fee_snapshots(position_id, block_number DESC);
CREATE INDEX IF NOT EXISTS idx_position_fee_wallet_time ON position_fee_snapshots(wallet_address, block_number DESC);

CREATE TABLE IF NOT EXISTS alert_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dedupe_key TEXT NOT NULL, severity TEXT NOT NULL,
    title TEXT NOT NULL, message TEXT NOT NULL, observed_at TEXT NOT NULL,
    evidence_json TEXT NOT NULL, recommended_checks_json TEXT NOT NULL,
    delivery_status TEXT NOT NULL DEFAULT 'pending'
);
CREATE INDEX IF NOT EXISTS idx_alert_events_time ON alert_events(observed_at DESC);
CREATE INDEX IF NOT EXISTS idx_alert_events_dedupe ON alert_events(dedupe_key, observed_at DESC);

CREATE TABLE IF NOT EXISTS decision_journal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    position_id TEXT, decision TEXT NOT NULL, rationale TEXT NOT NULL,
    created_at TEXT NOT NULL, evidence_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS provider_payloads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL, entity_id TEXT NOT NULL, fetched_at TEXT NOT NULL,
    payload_json TEXT NOT NULL, payload_hash TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_provider_payload_entity_time ON provider_payloads(entity_id, fetched_at DESC);
\n\nCREATE TABLE IF NOT EXISTS pool_activity_snapshots (\n    id INTEGER PRIMARY KEY AUTOINCREMENT,\n    pool_id TEXT NOT NULL, block_number INTEGER NOT NULL, block_hash TEXT NOT NULL,\n    block_timestamp INTEGER NOT NULL, window TEXT NOT NULL,\n    from_block INTEGER NOT NULL, to_block INTEGER NOT NULL, swap_count INTEGER NOT NULL,\n    volume_usd_estimated REAL, fees_usd_estimated REAL,\n    fee_token0_raw_estimated TEXT, fee_token1_raw_estimated TEXT,\n    volume_token0_raw TEXT, volume_token1_raw TEXT,\n    method TEXT NOT NULL, data_status TEXT NOT NULL, raw_ref TEXT\n);\nCREATE INDEX IF NOT EXISTS idx_pool_activity_time ON pool_activity_snapshots(pool_id, block_timestamp DESC);\n