SELECT
    DATE_FORMAT(order_date, '%Y-%m') AS month_year,

    COUNT(order_id) AS total_orders,

    SUM(CASE
        WHEN order_status = 'Canceled_By_Client' THEN 1
        ELSE 0
    END) AS canceled_orders_count,

    ROUND(
        (SUM(CASE
            WHEN order_status = 'Canceled_By_Client' THEN 1
            ELSE 0
        END) * 100.0 / COUNT(order_id)),
    2) AS cancellation_rate_pct

FROM FlightOrder
GROUP BY DATE_FORMAT(order_date, '%Y-%m')
ORDER BY month_year DESC;