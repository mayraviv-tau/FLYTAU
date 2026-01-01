/*
  REPORT 2: Revenue Analysis (By Plane & Class)
  Goal: Calculate total earnings from ticket sales.
   
  How it works:
  - We look at the order status to see how much money we actually kept.
  - Active/Completed = Full ticket price.
  - Canceled by Client = We keep 5% fee.
  - Canceled by Company = 0 (we refunded them).
  - Used CAST(DECIMAL) to force the result to 2 decimal places (money format).
*/

SELECT 
    p.size_category,       -- Group by Size (Large vs Small)
    p.manufacturer,        -- Group by Maker (Boeing, Airbus)
    t.class_type,          -- Group by Class (Economy, Business)
    
    -- Calculate total revenue
    -- Using CAST to ensure we get a clean money format (e.g., 100.50)
    CAST(
        SUM(
            CASE 
                WHEN fo.order_status IN ('Active', 'Completed') THEN t.price
                WHEN fo.order_status = 'Canceled_By_Client' THEN t.price * 0.05
                ELSE 0 -- Full refund if company canceled
            END
        ) AS DECIMAL(10, 2)
    ) AS total_revenue

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