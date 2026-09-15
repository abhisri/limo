-- LIMO Agent Bus — Postgres Schema
--
-- This creates the tables for the Agent Bus task dispatch system.
-- Loaded automatically by Postgres on first startup via docker-entrypoint-initdb.d.

-- ── Tasks ─────────────────────────────────────────────────────────
-- Each row is a task submitted by an agent to the bus.
CREATE TABLE IF NOT EXISTS agent_bus_tasks (
    id              BIGSERIAL PRIMARY KEY,
    task_id         UUID DEFAULT gen_random_uuid() UNIQUE NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at      TIMESTAMPTZ DEFAULT now() NOT NULL,

    -- Routing
    source_domain   TEXT NOT NULL,           -- e.g., 'Finance', 'Legal'
    target_domain   TEXT,                    -- NULL = bus decides routing
    intent          TEXT NOT NULL,           -- e.g., 'store_memory', 'query_graph', 'run_workflow'

    -- Payload
    payload         JSONB NOT NULL,          -- Task-specific data

    -- State machine: pending → claimed → done | failed | dead_letter
    status          TEXT DEFAULT 'pending' NOT NULL
                    CHECK (status IN ('pending', 'claimed', 'done', 'failed', 'dead_letter')),

    -- Claim tracking
    claimed_by      TEXT,                    -- Which agent/worker claimed this
    claimed_at      TIMESTAMPTZ,
    lease_expires   TIMESTAMPTZ,            -- If lease expires, task returns to pending

    -- Result
    result          JSONB,                   -- Response payload when done
    error           TEXT,                    -- Error message if failed

    -- Retry tracking
    attempt         INT DEFAULT 0 NOT NULL,
    max_attempts    INT DEFAULT 3 NOT NULL,

    -- Idempotency
    idempotency_key TEXT                     -- Optional: prevents duplicate task submission
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_tasks_status ON agent_bus_tasks (status);
CREATE INDEX IF NOT EXISTS idx_tasks_target ON agent_bus_tasks (target_domain, status);
CREATE INDEX IF NOT EXISTS idx_tasks_source ON agent_bus_tasks (source_domain);
CREATE INDEX IF NOT EXISTS idx_tasks_created ON agent_bus_tasks (created_at);
CREATE INDEX IF NOT EXISTS idx_tasks_idempotency ON agent_bus_tasks (idempotency_key) WHERE idempotency_key IS NOT NULL;

-- ── Events ────────────────────────────────────────────────────────
-- Audit trail. Every state change on a task produces an event.
CREATE TABLE IF NOT EXISTS agent_bus_events (
    id              BIGSERIAL PRIMARY KEY,
    task_id         UUID REFERENCES agent_bus_tasks(task_id) NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT now() NOT NULL,
    event_type      TEXT NOT NULL,            -- e.g., 'created', 'claimed', 'completed', 'failed', 'retried'
    actor           TEXT,                     -- Who triggered this event
    detail          JSONB                     -- Event-specific data
);

CREATE INDEX IF NOT EXISTS idx_events_task ON agent_bus_events (task_id);
CREATE INDEX IF NOT EXISTS idx_events_type ON agent_bus_events (event_type);

-- ── Helper: auto-update updated_at ───────────────────────────────
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_tasks_updated_at
    BEFORE UPDATE ON agent_bus_tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();
