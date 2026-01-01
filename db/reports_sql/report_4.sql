/*
  REPORT 4: Monthly Client Cancellation Rate
  -------------------------------------------------------
  Objective: Monitor the percentage of orders canceled BY THE CLIENT per month.
  Return: Month, Cancellation Rate.
*/

SELECT 
    DATE_FORMAT(order_date, '%Y-%m') AS month_year,
    
    ROUND(
        (SUM(CASE 
            WHEN order_status = 'Canceled_By_Client' THEN 1 
            ELSE 0 
        END) * 100.0 / COUNT(order_id)), 
    2) AS cancellation_rate_pct

FROM FlightOrder
GROUP BY DATE_FORMAT(order_date, '%Y-%m')
ORDER BY month_year DESC;