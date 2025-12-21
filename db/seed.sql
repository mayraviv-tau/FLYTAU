-- MANAGERS (At least 2 required)
INSERT INTO Manager (id_number, first_name_hebrew, last_name_hebrew, start_date, phone_number, city, street, house_number, account_password) VALUES
('100000001', 'משה', 'כהן', '2020-01-01', '050-1111111', 'Tel Aviv', 'Herzl', '1', 'pass123'),
('100000002', 'שרה', 'לוי', '2021-05-15', '052-2222222', 'Haifa', 'Allenby', '12', 'pass456');

--  PILOTS (10 required)
INSERT INTO Pilot (id_number, first_name_hebrew, last_name_hebrew, start_date, phone_number, is_long_haul_qualified) VALUES
('300000001', 'דני', 'שפירא', '2019-01-01', '050-3000001', TRUE),
('300000002', 'רון', 'ארד', '2019-01-01', '050-3000002', TRUE),
('300000003', 'יעל', 'רום', '2020-01-01', '050-3000003', TRUE),
('300000004', 'אילן', 'רמון', '2018-01-01', '050-3000004', TRUE),
('300000005', 'אסף', 'רמון', '2021-01-01', '050-3000005', TRUE),
('300000006', 'גיורא', 'אפשטיין', '2022-01-01', '050-3000006', FALSE), -- Short haul only
('300000007', 'אמיר', 'נחומי', '2022-01-01', '050-3000007', FALSE),
('300000008', 'רן', 'פקר', '2023-01-01', '050-3000008', FALSE),
('300000009', 'איתן', 'בן-אליהו', '2023-01-01', '050-3000009', FALSE),
('300000010', 'עידו', 'נחושתן', '2023-01-01', '050-3000010', FALSE);

-- FLIGHT ATTENDANTS (20 required)
INSERT INTO FlightAttendant (id_number, first_name_hebrew, last_name_hebrew, start_date, phone_number, is_long_haul_qualified) VALUES
('400000001', 'נועה', 'קירל', '2020-01-01', '050-4000001', TRUE),
('400000002', 'נטע', 'ברזילי', '2020-01-01', '050-4000002', TRUE),
('400000003', 'עומר', 'אדם', '2020-01-01', '050-4000003', TRUE),
('400000004', 'עדן', 'בן זקן', '2020-01-01', '050-4000004', TRUE),
('400000005', 'סטטיק', 'בן אל', '2020-01-01', '050-4000005', TRUE),
('400000006', 'בן', 'אל תבורי', '2020-01-01', '050-4000006', TRUE),
('400000007', 'אנה', 'זק', '2021-01-01', '050-4000007', TRUE),
('400000008', 'אגם', 'בוחבוט', '2021-01-01', '050-4000008', TRUE),
('400000009', 'מרגי', 'יהונתן', '2021-01-01', '050-4000009', TRUE),
('400000010', 'רביב', 'כנר', '2021-01-01', '050-4000010', FALSE),
('400000011', 'טונה', 'איתי', '2022-01-01', '050-4000011', FALSE),
('400000012', 'רביד', 'פלוטניק', '2022-01-01', '050-4000012', FALSE),
('400000013', 'יסמין', 'מועלם', '2022-01-01', '050-4000013', FALSE),
('400000014', 'חנן', 'בן ארי', '2022-01-01', '050-4000014', FALSE),
('400000015', 'עידן', 'רייכל', '2022-01-01', '050-4000015', FALSE),
('400000016', 'שלמה', 'ארצי', '2023-01-01', '050-4000016', FALSE),
('400000017', 'אריק', 'איינשטיין', '2023-01-01', '050-4000017', FALSE),
('400000018', 'גידי', 'גוב', '2023-01-01', '050-4000018', FALSE),
('400000019', 'יהודית', 'רביץ', '2023-01-01', '050-4000019', FALSE),
('400000020', 'ריטה', 'יהאן', '2023-01-01', '050-4000020', FALSE);

-- FLIGHT LINES (Routes)
INSERT INTO FlightLine (origin_airport, destination_airport, flight_duration) VALUES
('TLV', 'JFK', 12.5), -- Long Haul
('JFK', 'TLV', 11.0), -- Long Haul
('TLV', 'LHR', 5.5),  -- Short Haul
('LHR', 'TLV', 5.0),  -- Short Haul
('TLV', 'ETM', 1.0),  -- Short Haul
('ETM', 'TLV', 1.0);

-- PLANES (6 required)
INSERT INTO Plane (plane_id, manufacturer, size_category, acquisition_date) VALUES
(1, 'Boeing', 'Large', '2018-01-01'),
(2, 'Boeing', 'Large', '2019-06-15'),
(3, 'Airbus', 'Large', '2020-03-10'),
(4, 'Airbus', 'Small', '2021-11-20'),
(5, 'Dassault', 'Small', '2022-02-28'),
(6, 'Dassault', 'Small', '2023-08-05');


-- 4. PLANE CLASSES & SEATS

-- ---------------------------------------------
-- PLANE 1: Boeing (Large)
-- ---------------------------------------------
INSERT INTO PlaneClass (plane_id, class_type, rows_count, cols_count) VALUES
(1, 'Business', 5, 4), -- 20 Business seats
(1, 'Economy', 30, 6); -- 180 Economy seats

-- Sample Seats for Plane 1
INSERT INTO Seat (plane_id, class_type, seat_number) VALUES 
(1, 'Business', '1A'), (1, 'Business', '1B'), (1, 'Business', '2A'),
(1, 'Economy', '10A'), (1, 'Economy', '10B'), (1, 'Economy', '10C'), (1, 'Economy', '11A');

-- ---------------------------------------------
-- PLANE 2: Boeing (Large) 
-- ---------------------------------------------
INSERT INTO PlaneClass (plane_id, class_type, rows_count, cols_count) VALUES
(2, 'Business', 6, 4), -- 24 Business seats
(2, 'Economy', 32, 6); -- 192 Economy seats

-- Sample Seats for Plane 2
INSERT INTO Seat (plane_id, class_type, seat_number) VALUES 
(2, 'Business', '1A'), (2, 'Business', '1B'), (2, 'Business', '2C'),
(2, 'Economy', '15A'), (2, 'Economy', '15B'), (2, 'Economy', '15C'), (2, 'Economy', '16D');

-- ---------------------------------------------
-- PLANE 3: Airbus (Large) 
-- ---------------------------------------------
INSERT INTO PlaneClass (plane_id, class_type, rows_count, cols_count) VALUES
(3, 'Business', 4, 4), -- 16 Business seats
(3, 'Economy', 28, 6); -- 168 Economy seats

-- Sample Seats for Plane 3
INSERT INTO Seat (plane_id, class_type, seat_number) VALUES 
(3, 'Business', '1A'), (3, 'Business', '1D'),
(3, 'Economy', '12A'), (3, 'Economy', '12B'), (3, 'Economy', '12E'), (3, 'Economy', '12F');

-- ---------------------------------------------
-- PLANE 4: Airbus (Small) 
-- ---------------------------------------------
INSERT INTO PlaneClass (plane_id, class_type, rows_count, cols_count) VALUES
(4, 'Economy', 20, 4); -- 80 Economy seats

-- Sample Seats for Plane 4
INSERT INTO Seat (plane_id, class_type, seat_number) VALUES 
(4, 'Economy', '1A'), (4, 'Economy', '1B'),
(4, 'Economy', '5A'), (4, 'Economy', '5B'), (4, 'Economy', '5C');

-- ---------------------------------------------
-- PLANE 5: Dassault (Small) 
-- ---------------------------------------------
INSERT INTO PlaneClass (plane_id, class_type, rows_count, cols_count) VALUES
(5, 'Economy', 18, 4); -- 72 Economy seats

-- Sample Seats for Plane 5
INSERT INTO Seat (plane_id, class_type, seat_number) VALUES 
(5, 'Economy', '1A'), (5, 'Economy', '1C'),
(5, 'Economy', '8A'), (5, 'Economy', '8B');

-- ---------------------------------------------
-- PLANE 6: Dassault (Small) 
-- ---------------------------------------------
INSERT INTO PlaneClass (plane_id, class_type, rows_count, cols_count) VALUES
(6, 'Economy', 22, 4); -- 88 Economy seats

-- Sample Seats for Plane 6
INSERT INTO Seat (plane_id, class_type, seat_number) VALUES 
(6, 'Economy', '2A'), (6, 'Economy', '2B'),
(6, 'Economy', '10C'), (6, 'Economy', '10D');

-- CUSTOMERS (4 Total required: 2 Registered, 2 Guests)
INSERT INTO Customer (email, first_name_english, last_name_english) VALUES
('alice.thompson@gmail.com', 'Alice', 'Thompson'),
('michael.chen@yahoo.com', 'Michael', 'Chen'),
('sarah.miller@outlook.com', 'Sarah', 'Miller'),
('david.ross@gmail.com', 'David', 'Ross');

-- Registered Customers
INSERT INTO RegisteredCustomer (email, registration_date, birth_date, passport_number, account_password, balance) VALUES
('alice.thompson@gmail.com', '2024-01-15', '1992-06-23', 'A98273612', 'AlicePass1!', 1500.00),
('michael.chen@yahoo.com', '2024-03-10', '1988-11-05', 'C12345678', 'MikeFly2024', 200);


-- =============================================
-- FLIGHTS & CREW ASSIGNMENTS
-- =============================================

-- ---------------------------------------------------------
-- FLIGHT 1: Long Haul (TLV -> JFK) | Large Plane (ID 1)
-- Constraint: Needs 3 Pilots (Long Haul Qualified) & 6 FAs
-- ---------------------------------------------------------
INSERT INTO Flight (flight_id, origin_airport, destination_airport, plane_id, departure_datetime, manager_id, status) VALUES
(1, 'TLV', 'JFK', 1, '2026-04-01 08:00:00', '100000001', 'Active');

-- Crew for Flight 1 (Must be Long Haul Qualified)
INSERT INTO FlightPilotAssignment (flight_id, pilot_id) VALUES
(1, '300000001'), -- Qualified
(1, '300000002'), -- Qualified
(1, '300000003'); -- Qualified

INSERT INTO FlightAttendantAssignment (flight_id, flight_attendant_id) VALUES
(1, '400000001'), (1, '400000002'), (1, '400000003'), -- All Qualified
(1, '400000004'), (1, '400000005'), (1, '400000006');

-- ---------------------------------------------------------
-- FLIGHT 2: Short Haul (TLV -> ETM) | Small Plane (ID 4)
-- Constraint: Needs 2 Pilots & 3 FAs (Any qualification OK)
-- ---------------------------------------------------------
INSERT INTO Flight (flight_id, origin_airport, destination_airport, plane_id, departure_datetime, manager_id, status) VALUES
(2, 'TLV', 'ETM', 4, '2026-04-02 10:00:00', '100000001', 'Active');

-- Crew for Flight 2 (Can use non-qualified staff)
INSERT INTO FlightPilotAssignment (flight_id, pilot_id) VALUES
(2, '300000006'), -- Not Qualified (OK for short haul)
(2, '300000007'); -- Not Qualified

INSERT INTO FlightAttendantAssignment (flight_id, flight_attendant_id) VALUES
(2, '400000010'), (2, '400000011'), (2, '400000012');

-- ---------------------------------------------------------
-- FLIGHT 3: Short Haul (TLV -> LHR) | Large Plane (ID 2)
-- Constraint: Needs 3 Pilots & 6 FAs (Any qualification OK)
-- ---------------------------------------------------------
INSERT INTO Flight (flight_id, origin_airport, destination_airport, plane_id, departure_datetime, manager_id, status) VALUES
(3, 'TLV', 'LHR', 2, '2026-04-05 14:00:00', '100000002', 'Active');

-- Crew for Flight 3 (Mixed qualifications OK)
INSERT INTO FlightPilotAssignment (flight_id, pilot_id) VALUES
(3, '300000004'), -- Qualified
(3, '300000008'), -- Not Qualified
(3, '300000009'); -- Not Qualified

INSERT INTO FlightAttendantAssignment (flight_id, flight_attendant_id) VALUES
(3, '400000007'), (3, '400000008'), (3, '400000013'), 
(3, '400000014'), (3, '400000015'), (3, '400000016');

-- ---------------------------------------------------------
-- FLIGHT 4: Short Haul (ETM -> TLV) | Small Plane (ID 5)
-- Constraint: Needs 2 Pilots & 3 FAs
-- ---------------------------------------------------------
INSERT INTO Flight (flight_id, origin_airport, destination_airport, plane_id, departure_datetime, manager_id, status) VALUES
(4, 'ETM', 'TLV', 5, '2026-04-06 16:00:00', '100000002', 'Active');

-- Crew for Flight 4
INSERT INTO FlightPilotAssignment (flight_id, pilot_id) VALUES
(4, '300000005'), -- Qualified
(4, '300000010'); -- Not Qualified

INSERT INTO FlightAttendantAssignment (flight_id, flight_attendant_id) VALUES
(4, '400000009'), (4, '400000019'), (4, '400000020');

-- =============================================
-- 10. ORDERS & TICKETS (4 Orders required)
-- =============================================

-- ---------------------------------------------------------
-- ORDER 1: Alice (Registered)
-- Flight 1 (TLV->JFK), 1 Business Class Ticket
-- ---------------------------------------------------------
INSERT INTO FlightOrder (customer_email, flight_id, order_date, order_status, total_payment) 
VALUES ('alice.thompson@gmail.com', 1, '2026-01-15 10:00:00', 'Active', 1500.00);

INSERT INTO Ticket (order_id, plane_id, class_type, seat_number, price) 
VALUES (LAST_INSERT_ID(), 1, 'Business', '1A', 1500.00);

-- ---------------------------------------------------------
-- ORDER 2: Sarah (Guest)
-- Flight 1 (TLV->JFK), 1 Economy Class Ticket
-- ---------------------------------------------------------
INSERT INTO FlightOrder (customer_email, flight_id, order_date, order_status, total_payment) 
VALUES ('sarah.miller@outlook.com', 1, '2026-01-16 12:00:00', 'Active', 800.00);

INSERT INTO Ticket (order_id, plane_id, class_type, seat_number, price) 
VALUES (LAST_INSERT_ID(), 1, 'Economy', '10A', 800.00);

-- ---------------------------------------------------------
-- ORDER 3: Michael (Registered)
-- Flight 2 (TLV->ETM), 2 Economy Class Tickets
-- ---------------------------------------------------------
INSERT INTO FlightOrder (customer_email, flight_id, order_date, order_status, total_payment) 
VALUES ('michael.chen@yahoo.com', 2, '2026-01-20 09:00:00', 'Active', 200.00);

SET @michael_order_id = LAST_INSERT_ID();

INSERT INTO Ticket (order_id, plane_id, class_type, seat_number, price) VALUES 
(@michael_order_id, 4, 'Economy', '5A', 100.00),
(@michael_order_id, 4, 'Economy', '5B', 100.00);

-- ---------------------------------------------------------
-- ORDER 4: David (Guest) -> CANCELED
-- Flight 1 (TLV->JFK). Was 800.00, canceled by client.
-- Fee: 5% of 800 = 40.00.
-- ---------------------------------------------------------
INSERT INTO FlightOrder (customer_email, flight_id, order_date, order_status, total_payment) 
VALUES ('david.ross@gmail.com', 1, '2026-01-10 08:00:00', 'Canceled_By_Client', 40.00);

INSERT INTO Ticket (order_id, plane_id, class_type, seat_number, price) 
VALUES (LAST_INSERT_ID(), 1, 'Economy', '10B', 800.00);