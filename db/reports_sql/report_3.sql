SELECT 
    'Pilot' AS role,
    p.id_number,
    p.first_name_hebrew,
    p.last_name_hebrew,
    COALESCE(SUM(CASE WHEN fl.flight_duration > 6 THEN fl.flight_duration ELSE 0 END), 0) AS long_haul_hours,
    COALESCE(SUM(CASE WHEN fl.flight_duration <= 6 THEN fl.flight_duration ELSE 0 END), 0) AS short_haul_hours

FROM Pilot p
LEFT JOIN FlightPilotAssignment fpa ON p.id_number = fpa.pilot_id
LEFT JOIN Flight f ON fpa.flight_id = f.flight_id AND f.status = 'Landed'
LEFT JOIN FlightLine fl ON f.origin_airport = fl.origin_airport 
                        AND f.destination_airport = fl.destination_airport
GROUP BY p.id_number, p.first_name_hebrew, p.last_name_hebrew

UNION ALL

SELECT 
    'Flight Attendant' AS role,
    fa.id_number,
    fa.first_name_hebrew,
    fa.last_name_hebrew,
    COALESCE(SUM(CASE WHEN fl.flight_duration > 6 THEN fl.flight_duration ELSE 0 END), 0) AS long_haul_hours,
    COALESCE(SUM(CASE WHEN fl.flight_duration <= 6 THEN fl.flight_duration ELSE 0 END), 0) AS short_haul_hours

FROM FlightAttendant fa
LEFT JOIN FlightAttendantAssignment faa ON fa.id_number = faa.flight_attendant_id
LEFT JOIN Flight f ON faa.flight_id = f.flight_id AND f.status = 'Landed'
LEFT JOIN FlightLine fl ON f.origin_airport = fl.origin_airport 
                        AND f.destination_airport = fl.destination_airport
GROUP BY fa.id_number, fa.first_name_hebrew, fa.last_name_hebrew

ORDER BY role DESC, last_name_hebrew ASC;