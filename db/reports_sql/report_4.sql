/*
  REPORT 4: Monthly Cancellation Rates
  -------------------------------------------------------
  Objective: Monitor the percentage of orders canceled per month.
  
  Logic:
  - Total Orders: All orders placed in that month.
  - Canceled Orders: Status is 'Canceled_By_Client' or 'Canceled_By_Company'.
  - Rate: (Canceled / Total) * 100.
*/

SELECT 
    -- Format Date as "YYYY-MM" for sorting and grouping
    DATE_FORMAT(order_date, '%Y-%m') AS month_year,
    
    -- 1. Count Total Orders (The Denominator)
    COUNT(order_id) AS total_orders,
    
    -- 2. Count Canceled Orders (The Numerator)
    SUM(CASE 
        WHEN order_status IN ('Canceled_By_Client', 'Canceled_By_Company') THEN 1 
        ELSE 0 
    END) AS canceled_orders_count,
    
    -- 3. Calculate Percentage
    ROUND(
        (SUM(CASE 
            WHEN order_status IN ('Canceled_By_Client', 'Canceled_By_Company') THEN 1 
            ELSE 0 
        END) * 100.0 / COUNT(order_id)), 
    2) AS cancellation_rate_pct

FROM FlightOrder
GROUP BY DATE_FORMAT(order_date, '%Y-%m')
ORDER BY month_year DESC;