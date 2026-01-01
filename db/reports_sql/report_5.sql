/*
  REPORT 5: Monthly Plane Activity Summary (Daily Utilization)
  ------------------------------------------------------------
  Objective: Operational report per plane per month.
  Updates:
  - Uses LEFT JOIN (Fixes issue where planes with only cancellations disappeared).
  - Ranking logic remains simple (Count DESC).
*/

SELECT 
    stats.month_year,
    stats.plane_id,
    stats.flights_performed,
    stats.flights_canceled,
    ROUND((stats.days_active / 30.0) * 100, 2) AS utilization_pct,
    -- Handle NULLs since we are now using a LEFT JOIN
    COALESCE(CONCAT(routes.origin_airport, ' -> ', routes.destination_airport), 'No Active Flights') AS dominant_route

FROM 
    (
        SELECT 
            DATE_FORMAT(f.departure_datetime, '%Y-%m') AS month_year,
            f.plane_id,
            SUM(CASE WHEN f.status IN ('Active', 'Landed') THEN 1 ELSE 0 END) AS flights_performed,
            SUM(CASE WHEN f.status = 'Canceled' THEN 1 ELSE 0 END) AS flights_canceled,
            COUNT(DISTINCT CASE 
                WHEN f.status IN ('Active', 'Landed') THEN DATE(f.departure_datetime) 
                ELSE NULL 
            END) AS days_active
        FROM Flight f
        GROUP BY DATE_FORMAT(f.departure_datetime, '%Y-%m'), f.plane_id
    ) AS stats

LEFT JOIN 
    (
        SELECT 
            DATE_FORMAT(departure_datetime, '%Y-%m') AS month_year,
            plane_id,
            origin_airport,
            destination_airport,
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
    AND routes.ranking = 1

ORDER BY stats.month_year DESC, stats.plane_id ASC;