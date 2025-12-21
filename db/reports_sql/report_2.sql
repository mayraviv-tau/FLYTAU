/*
  REPORT 2: Revenue Analysis (By Size, Manufacturer, Class)
  ----------------------------------------------------------
  Objective: Summarize total income derived from ticket sales.
  
  Key Logic:
  - We calculate "Realized Revenue" per ticket based on the Order Status.
  - Active/Completed Orders = Full Ticket Price.
  - Client Cancellations = 5% of Ticket Price (Fee).
  - Company Cancellations = 0 (Full Refund).
*/

SELECT 
    p.size_category,       -- Dimension 1: Plane Size (Large/Small)
    p.manufacturer,        -- Dimension 2: Manufacturer (Boeing/Airbus...)
    t.class_type,          -- Dimension 3: Class (Economy/Business)
    
    -- Calculate Revenue Per Ticket Group
    SUM(
        CASE 
            WHEN fo.order_status IN ('Active', 'Completed') THEN t.price
            WHEN fo.order_status = 'Canceled_By_Client' THEN t.price * 0.05
            ELSE 0 -- Canceled_By_Company or other status implies full refund
        END
    ) AS total_revenue,
    
    -- Optional: Count tickets involved to see volume vs value
    COUNT(t.seat_number) as tickets_sold_count

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