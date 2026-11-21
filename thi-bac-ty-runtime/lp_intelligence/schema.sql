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


CREATE TABLE IF NOT EXISTS pool_activity_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pool_id TEXT NOT NULL, block_number INTEGER NOT NULL, block_hash TEXT NOT NULL,
    block_timestamp INTEGER NOT NULL, window TEXT NOT NULL,
    from_block INTEGER NOT NULL, to_block INTEGER NOT NULL, swap_count INTEGER NOT NULL,
    volume_usd_estimated REAL, fees_usd_estimated REAL,
    fee_token0_raw_estimated TEXT, fee_token1_raw_estimated TEXT,
    volume_token0_raw TEXT, volume_token1_raw TEXT,
    method TEXT NOT NULL, data_status TEXT NOT NULL, raw_ref TEXT
);
CREATE INDEX IF NOT EXISTS idx_pool_activity_time ON pool_activity_snapshots(pool_id, block_timestamp DESC);


CREATE TABLE IF NOT EXISTS wallet_chain_baselines (
    wallet_address TEXT NOT NULL, chain_id TEXT NOT NULL, chain_name TEXT NOT NULL,
    baseline_block INTEGER NOT NULL, baseline_hash TEXT NOT NULL,
    baseline_timestamp TEXT NOT NULL, scan_from_block INTEGER NOT NULL,
    created_at TEXT NOT NULL, PRIMARY KEY(wallet_address, chain_id)
);
CREATE TABLE IF NOT EXISTS wallet_monitor_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT, wallet_address TEXT NOT NULL,
    observed_at TEXT NOT NULL, status TEXT NOT NULL, result_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_wallet_monitor_runs_wallet_time
ON wallet_monitor_runs(wallet_address, observed_at DESC);
CREATE TABLE IF NOT EXISTS xlayer_position_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT, wallet_address TEXT NOT NULL,
    token_id TEXT NOT NULL, block_number INTEGER NOT NULL, block_hash TEXT NOT NULL,
    block_timestamp INTEGER NOT NULL, pool_address TEXT, token0 TEXT, token1 TEXT,
    fee_tier INTEGER, tick_lower INTEGER, tick_upper INTEGER, current_tick INTEGER,
    liquidity_raw TEXT, tokens_owed0_raw TEXT, tokens_owed1_raw TEXT,
    range_status TEXT, verification TEXT NOT NULL, payload_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_xlayer_position_wallet_block
ON xlayer_position_snapshots(wallet_address, block_number DESC, token_id);


CREATE TABLE IF NOT EXISTS token_price_observations (
    id INTEGER PRIMARY KEY AUTOINCREMENT, chain_id TEXT NOT NULL,
    token_address TEXT NOT NULL, price_usd REAL NOT NULL CHECK(price_usd > 0),
    observed_at TEXT NOT NULL, fetched_at TEXT NOT NULL,
    source TEXT NOT NULL, source_url TEXT NOT NULL, data_status TEXT NOT NULL,
    raw_ref TEXT
);
CREATE INDEX IF NOT EXISTS idx_token_prices_lookup
ON token_price_observations(chain_id, token_address, observed_at DESC);

CREATE TABLE IF NOT EXISTS position_performance_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT, position_id TEXT NOT NULL,
    wallet_address TEXT NOT NULL, chain_id TEXT NOT NULL,
    block_number INTEGER NOT NULL, block_hash TEXT NOT NULL,
    observed_at TEXT NOT NULL, fetched_at TEXT NOT NULL,
    token0_address TEXT NOT NULL, token1_address TEXT NOT NULL,
    token0_symbol TEXT NOT NULL, token1_symbol TEXT NOT NULL,
    amount0 TEXT NOT NULL, amount1 TEXT NOT NULL,
    fees0 TEXT NOT NULL, fees1 TEXT NOT NULL,
    price0_usd REAL NOT NULL, price1_usd REAL NOT NULL,
    principal_usd REAL NOT NULL, unclaimed_fees_usd REAL NOT NULL,
    position_value_usd REAL NOT NULL, initial_capital_usd REAL,
    hodl_value_usd REAL, il_vs_hodl_usd REAL, il_vs_hodl_pct REAL,
    fee_adjusted_vs_hodl_usd REAL, pnl_before_claimed_fees_and_costs_usd REAL,
    fee_apr_24h_pct REAL, fee_apr_7d_pct REAL, fee_apr_30d_pct REAL,
    claimed_fees_usd REAL, gas_cost_usd REAL, rebalance_cost_usd REAL,
    data_status TEXT NOT NULL, methodology_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_perf_position_time
ON position_performance_snapshots(position_id, observed_at DESC);
CREATE INDEX IF NOT EXISTS idx_perf_wallet_time
ON position_performance_snapshots(wallet_address, observed_at DESC);
