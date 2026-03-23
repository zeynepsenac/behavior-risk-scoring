SELECT
    AVG(risk_score) AS original_avg,
    AVG(
        0.4 * payment_discipline_score +
        0.3 * income_stability_index +
        0.3 * financial_resilience_score
    ) AS predicted_avg,
    ABS(
        AVG(risk_score) -
        AVG(
            0.4 * payment_discipline_score +
            0.3 * income_stability_index +
            0.3 * financial_resilience_score
        )
    ) AS difference
FROM engineered_customers;