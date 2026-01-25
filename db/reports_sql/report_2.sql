SELECT
    p.size_category,
    p.manufacturer,
    t.class_type,

    CAST(
        SUM(
            CASE
                WHEN fo.order_status IN ('Active', 'Completed') THEN t.price
                WHEN fo.order_status = 'Canceled_By_Client' THEN t.price * 0.05
                ELSE 0
            END
        ) AS DECIMAL(10, 2)
    ) AS total_revenue,

    COUNT(t.seat_number) AS tickets_sold_count

FROM Ticket t
JOIN FlightOrder fo ON t.order_id = fo.order_id
JOIN Plane p ON t.plane_id = p.plane_id

GROUP BY
    p.size_category,
    p.manufacturer,
    t.class_type

ORDER BY
    p.size_category DESC,
    total_revenue DESC;