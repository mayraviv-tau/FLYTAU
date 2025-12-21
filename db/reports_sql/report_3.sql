/*
  REPORT 3: Staff Accumulated Flight Hours
  -------------------------------------------------------
  Objective: Track total flight hours for every employee, separated by 
             Short Haul (<= 6h) and Long Haul (> 6h).

  Structure:
  - Part A: Selects form Pilots table.
  - Part B: Selects from FlightAttendant table.
  - UNION ALL: Combines them into one list.
*/

SELECT 
    'Pilot' AS role,
    p.id_number,
    p.first_name_hebrew,
    p.last_name_hebrew,
    -- Calculate Long Haul Hours (> 6)
    COALESCE(SUM(CASE WHEN fl.flight_duration > 6 THEN fl.flight_duration ELSE 0 END), 0) AS long_haul_hours,
    -- Calculate Short Haul Hours (<= 6)
    COALESCE(SUM(CASE WHEN fl.flight_duration <= 6 THEN fl.flight_duration ELSE 0 END), 0) AS short_haul_hours,
    -- Total
    COALESCE(SUM(fl.flight_duration), 0) AS total_hours

FROM Pilot p
-- Join to Assignments (LEFT JOIN to include pilots with 0 hours)
LEFT JOIN FlightPilotAssignment fpa ON p.id_number = fpa.pilot_id
LEFT JOIN Flight f ON fpa.flight_id = f.flight_id AND f.status IN ('Active', 'Landed')
LEFT JOIN FlightLine fl ON f.origin_airport = fl.origin_airport 
                        AND f.destination_airport = fl.destination_airport
GROUP BY p.id_number, p.first_name_hebrew, p.last_name_hebrew

UNION ALL

SELECT 
    'Flight Attendant' AS role,
    fa.id_number,
    fa.first_name_hebrew,
    fa.last_name_hebrew,
    -- Calculate Long Haul Hours (> 6)
    COALESCE(SUM(CASE WHEN fl.flight_duration > 6 THEN fl.flight_duration ELSE 0 END), 0) AS long_haul_hours,
    -- Calculate Short Haul Hours (<= 6)
    COALESCE(SUM(CASE WHEN fl.flight_duration <= 6 THEN fl.flight_duration ELSE 0 END), 0) AS short_haul_hours,
    -- Total
    COALESCE(SUM(fl.flight_duration), 0) AS total_hours

FROM FlightAttendant fa
-- Join to Assignments
LEFT JOIN FlightAttendantAssignment faa ON fa.id_number = faa.flight_attendant_id
LEFT JOIN Flight f ON faa.flight_id = f.flight_id AND f.status IN ('Active', 'Landed')
LEFT JOIN FlightLine fl ON f.origin_airport = fl.origin_airport 
                        AND f.destination_airport = fl.destination_airport
GROUP BY fa.id_number, fa.first_name_hebrew, fa.last_name_hebrew

ORDER BY role DESC, total_hours DESC;