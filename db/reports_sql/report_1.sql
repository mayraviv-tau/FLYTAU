/*
  REPORT 1: Average Occupancy of Flights That Took Place
  -------------------------------------------------------
  Objective: Calculate the average ***percentage*** of occupied seats for all flights 
             that have been completed ('Landed').

  Logic Breakdown:
  1. Inner Query ('per_flight_stats'):
     - Calculates the total capacity of the specific plane used (sum of rows * cols for all classes).
     - Counts the number of valid tickets sold (ignoring canceled orders).
     - Computes the percentage: (Sold Tickets / Total Capacity) * 100.
  
  2. Outer Query:
     - Aggregates the percentages from all relevant flights to find the system-wide average.
     - Rounds the result to 2 decimal places for clean reporting.
*/

SELECT 
    ROUND(AVG(flight_occupancy_pct), 2) AS average_system_occupancy
FROM (
    SELECT 
        f.flight_id,
        (
          -- Count unique tickets associated with valid orders.
          -- We use DISTINCT on the ticket's primary key components to prevent duplicate counting.
          COUNT(DISTINCT t.order_id, t.plane_id, t.class_type, t.seat_number) 
          * 100.0 / NULLIF(pc.total_seats, 0)
        ) AS flight_occupancy_pct
    FROM Flight f
    
    -- 1. Calculate total capacity per plane dynamically
    -- (Required because capacity is derived from rows * cols in PlaneClass)
    JOIN (
        SELECT plane_id, SUM(rows_count * cols_count) AS total_seats
        FROM PlaneClass
        GROUP BY plane_id
    ) pc ON f.plane_id = pc.plane_id
    
    -- 2. Join Orders: Only consider 'Active' or 'Completed' orders 
    -- (We explicitly exclude 'Canceled' orders to ensure occupancy is real)
    LEFT JOIN FlightOrder fo
        ON f.flight_id = fo.flight_id
       AND fo.order_status IN ('Active', 'Completed')
       
    -- 3. Join Tickets: Link the specific tickets to the orders
    LEFT JOIN Ticket t
        ON fo.order_id = t.order_id
       AND t.plane_id = f.plane_id
       
    -- Filter: Only include flights that have actually taken place
    WHERE f.status IN ('Landed')
    
    GROUP BY f.flight_id, pc.total_seats
) AS per_flight_stats;