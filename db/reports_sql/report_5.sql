/*
  REPORT 5: Monthly Plane Activity Summary (Daily Utilization)
  ------------------------------------------------------------
  Objective: Operational report per plane per month.
  
  Metrics:
  1. Flights Performed: Count of 'Active' or 'Landed'.
  2. Flights Canceled: Count of 'Canceled'.
  3. Utilization %: (Days Flown / 30) * 100.
  4. Dominant Route: Most frequent Origin->Dest pair.
*/

SELECT 
    stats.month_year,
    stats.plane_id,
    
    -- Metric 1: Flights Performed
    stats.flights_performed,
    
    -- Metric 2: Flights Canceled
    stats.flights_canceled,
    
    -- Metric 3: Utilization % (Days Active / 30)
    ROUND((stats.days_active / 30.0) * 100, 2) AS utilization_pct,
    
    -- Metric 4: Dominant Route
    CONCAT(routes.origin_airport, ' -> ', routes.destination_airport) AS dominant_route

FROM 
    -- SUBQUERY 1: Calculate Counts and Utilization
    (
        SELECT 
            DATE_FORMAT(f.departure_datetime, '%Y-%m') AS month_year,
            f.plane_id,
            
            -- Count Performed
            SUM(CASE WHEN f.status IN ('Active', 'Landed') THEN 1 ELSE 0 END) AS flights_performed,
            
            -- Count Canceled
            SUM(CASE WHEN f.status = 'Canceled' THEN 1 ELSE 0 END) AS flights_canceled,
            
            -- Count Unique Active Days (Utilization Numerator)
            COUNT(DISTINCT CASE 
                WHEN f.status IN ('Active', 'Landed') THEN DATE(f.departure_datetime) 
                ELSE NULL 
            END) AS days_active
            
        FROM Flight f
        GROUP BY DATE_FORMAT(f.departure_datetime, '%Y-%m'), f.plane_id
    ) AS stats

JOIN 
    -- SUBQUERY 2: Find the Dominant Route (Ranked #1)
    (
        SELECT 
            DATE_FORMAT(departure_datetime, '%Y-%m') AS month_year,
            plane_id,
            origin_airport,
            destination_airport,
            -- Rank routes by frequency (Desc)
            ROW_NUMBER() OVER (
                PARTITION BY DATE_FORMAT(departure_datetime, '%Y-%m'), plane_id 
                ORDER BY COUNT(*) DESC
            ) as ranking
        FROM Flight
        WHERE status IN ('Active', 'Landed') 
        GROUP BY DATE_FORMAT(departure_datetime, '%Y-%m'), plane_id, origin_airport, destination_airport
    ) AS routes 
    
    ON stats.plane_id = routes.plane_id 
    AND stats.month_year = routes.month_year 
    AND routes.ranking = 1 -- Select only the #1 route

ORDER BY stats.month_year DESC, stats.plane_id ASC;