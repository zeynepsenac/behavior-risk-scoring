CREATE TABLE IF NOT EXISTS customer_raw_events (
    event_id BIGSERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    event_type VARCHAR(50),
    event_value NUMERIC,
    event_time TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_event_customer_time
ON customer_raw_events(customer_id, event_time DESC);