CREATE TABLE prediction_history (
    prediction_id BIGSERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    risk_score NUMERIC(5,2) NOT NULL,
    risk_band VARCHAR(10) NOT NULL,
    model_version VARCHAR(20) NOT NULL,
    prediction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE prediction_history
ADD CONSTRAINT fk_customer
FOREIGN KEY (customer_id)
REFERENCES engineered_customers(customer_id);

CREATE INDEX idx_prediction_customer_time
ON prediction_history(customer_id, prediction_time DESC);