/*
  REPORT 1: Average Occupancy
  Calculates the average % of seats taken on flights that have already landed.
  
  Logic:
  1. Inner query: Calculate the occupancy % for each specific flight (tickets / total seats).
  2. Outer query: Just take the average of all those percentages.
*/

SELECT 
    ROUND(AVG(flight_occupancy_pct), 2) AS average_system_occupancy
FROM (
    SELECT 
        f.flight_id,
        (
          COUNT(DISTINCT t.ticket_id) 
          * 100.0 / NULLIF(pc.total_seats, 0)
        ) AS flight_occupancy_pct
    FROM Flight f
    
    -- 1. Calculate total seats (capacity) per plane
    JOIN (
        SELECT plane_id, SUM(rows_count * cols_count) AS total_seats
        FROM PlaneClass
        GROUP BY plane_id
    ) pc ON f.plane_id = pc.plane_id
    
    -- 2. Join valid orders (only ones that are actually completed)
    LEFT JOIN FlightOrder fo
        ON f.flight_id = fo.flight_id
       AND fo.order_status = 'Completed'
       
    -- 3. Join tickets so we can count the passengers
    LEFT JOIN Ticket t
        ON fo.order_id = t.order_id
       
    WHERE f.status = 'Landed'
    
    GROUP BY f.flight_id, pc.total_seats
) AS per_flight_stats;