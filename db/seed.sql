-- =============================================
-- AIRLINE MANAGEMENT SYSTEM - SEED DATA
-- =============================================

-- =============================================
-- STAFF & ASSETS
-- =============================================
INSERT INTO Manager (id_number, first_name_hebrew, last_name_hebrew, start_date, phone_number, city, street, house_number, account_password) VALUES
('100000001', 'משה', 'כהן', '2020-01-01', '050-1111111', 'Tel Aviv', 'Herzl', '1', 'pass123'),
('100000002', 'שרה', 'לוי', '2021-05-15', '052-2222222', 'Haifa', 'Allenby', '12', 'pass456');

INSERT INTO Pilot (id_number, first_name_hebrew, last_name_hebrew, start_date, phone_number, is_long_haul_qualified) VALUES
('300000001', 'דני', 'שפירא', '2019-01-01', '050-3000001', TRUE),
('300000002', 'רון', 'ארד', '2019-01-01', '050-3000002', TRUE),
('300000003', 'יעל', 'רום', '2020-01-01', '050-3000003', TRUE),
('300000004', 'אילן', 'רמון', '2018-01-01', '050-3000004', TRUE),
('300000005', 'אסף', 'רמון', '2021-01-01', '050-3000005', TRUE),
('300000006', 'גיורא', 'אפשטיין', '2022-01-01', '050-3000006', FALSE),
('300000007', 'אמיר', 'נחומי', '2022-01-01', '050-3000007', FALSE),
('300000008', 'רן', 'פקר', '2023-01-01', '050-3000008', FALSE),
('300000009', 'איתן', 'בן-אליהו', '2023-01-01', '050-3000009', FALSE),
('300000010', 'עידו', 'נחושתן', '2023-01-01', '050-3000010', FALSE);

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
('400000011', 'שירה', 'כהן', '2022-01-01', '050-4000011', TRUE),
('400000012', 'מיכל', 'לוי', '2022-01-01', '050-4000012', TRUE),
('400000013', 'תמר', 'דוד', '2022-01-01', '050-4000013', TRUE),
('400000014', 'רותם', 'ישראלי', '2022-01-01', '050-4000014', FALSE),
('400000015', 'ליאור', 'כהן', '2022-01-01', '050-4000015', FALSE),
('400000016', 'אור', 'שלום', '2023-01-01', '050-4000016', TRUE),
('400000017', 'מור', 'אברהם', '2023-01-01', '050-4000017', FALSE),
('400000018', 'יובל', 'יעקב', '2023-01-01', '050-4000018', FALSE),
('400000019', 'רוני', 'משה', '2023-01-01', '050-4000019', FALSE),
('400000020', 'דנה', 'אהרון', '2023-01-01', '050-4000020', FALSE);

INSERT INTO FlightLine (origin_airport, destination_airport, flight_duration) VALUES
('TLV', 'JFK', 12.5), ('JFK', 'TLV', 11.0),
('TLV', 'LHR', 5.5),  ('LHR', 'TLV', 5.0),
('TLV', 'ETM', 1.0),  ('ETM', 'TLV', 1.0);

INSERT INTO Plane (plane_id, manufacturer, size_category, acquisition_date) VALUES
(1, 'Boeing', 'Large', '2018-01-01'),
(2, 'Boeing', 'Large', '2019-06-15'),
(3, 'Airbus', 'Large', '2020-03-10'),
(4, 'Airbus', 'Small', '2021-11-20'),
(5, 'Dassault', 'Small', '2022-02-28'),
(6, 'Boeing', 'Large', '2023-05-10');

-- =============================================
-- PLANE CONFIGURATION
-- =============================================
INSERT INTO PlaneClass VALUES (1, 'Business', 5, 4), (1, 'Economy', 30, 6);
INSERT INTO Seat VALUES (1, 'Business', '1A'), (1, 'Business', '1B'), (1, 'Economy', '10A'), (1, 'Economy', '10B');

INSERT INTO PlaneClass VALUES (3, 'Business', 4, 4), (3, 'Economy', 28, 6);
INSERT INTO Seat VALUES (3, 'Business', '1A'), (3, 'Business', '1B'), (3, 'Economy', '12A'), (3, 'Economy', '12B');

INSERT INTO PlaneClass VALUES (4, 'Economy', 20, 4);
INSERT INTO Seat VALUES (4, 'Economy', '1A'), (4, 'Economy', '1B');

INSERT INTO PlaneClass VALUES (5, 'Economy', 18, 4);
INSERT INTO Seat VALUES (5, 'Economy', '1A'), (5, 'Economy', '1B');

INSERT INTO PlaneClass VALUES (2, 'Business', 6, 4), (2, 'Economy', 32, 6);
INSERT INTO Seat VALUES (2, 'Business', '1A'), (2, 'Business', '1B'), (2, 'Economy', '11A'), (2, 'Economy', '11B');

INSERT INTO PlaneClass VALUES (6, 'Business', 5, 4), (6, 'Economy', 30, 6);
INSERT INTO Seat VALUES (6, 'Business', '1A'), (6, 'Business', '1B'), (6, 'Economy', '10A'), (6, 'Economy', '10B');

-- =============================================
-- CUSTOMERS
-- =============================================
INSERT INTO Customer (email, first_name_english, last_name_english) VALUES
('c1@test.com', 'Alice', 'One'), 
('c2@test.com', 'Bob', 'Two'), 
('c3@test.com', 'Charlie', 'Three'),
('c4@test.com', 'David', 'Four'), 
('c5@test.com', 'Eve', 'Five');

INSERT INTO RegisteredCustomer (email, registration_date, birth_date, passport_number, account_password, balance) VALUES
('c1@test.com', '2023-01-01', '1990-01-01', 'P1', 'pass', 1000),
('c2@test.com', '2023-01-01', '1990-01-01', 'P2', 'pass', 1000);

-- =============================================
-- FLIGHTS
-- =============================================
INSERT INTO Flight VALUES (101, 'TLV', 'JFK', 1, '2025-11-10 08:00:00', '100000001', 'Landed');
INSERT INTO Flight VALUES (102, 'TLV', 'LHR', 3, '2025-12-15 09:00:00', '100000001', 'Landed');
INSERT INTO Flight VALUES (103, 'TLV', 'ETM', 4, '2026-01-20 10:00:00', '100000001', 'Landed');
INSERT INTO Flight VALUES (104, 'ETM', 'TLV', 5, '2026-02-10 11:00:00', '100000002', 'Active');
INSERT INTO Flight VALUES (105, 'LHR', 'TLV', 1, '2026-03-05 14:00:00', '100000002', 'Active');
INSERT INTO Flight VALUES (106, 'TLV', 'JFK', 2, '2026-04-15 10:00:00', '100000001', 'Active');
INSERT INTO Flight VALUES (107, 'JFK', 'TLV', 6, '2026-05-20 08:00:00', '100000002', 'Active');

-- =============================================
-- CREW ASSIGNMENTS (With explicit column names to fix previous error)
-- =============================================
INSERT INTO FlightPilotAssignment (flight_id, pilot_id) VALUES 
(101, '300000001'), (101, '300000002'), 
(102, '300000003'), (102, '300000004'), 
(103, '300000006'), 
(104, '300000007'), 
(105, '300000008'),
(106, '300000001'), (106, '300000002'), (106, '300000003'),
(107, '300000004'), (107, '300000005');

INSERT INTO FlightAttendantAssignment (flight_id, flight_attendant_id) VALUES
(101, '400000001'), (101, '400000002'),
(102, '400000003'), (102, '400000004'),
(103, '400000005'),
(104, '400000006'),
(105, '400000007'),
(106, '400000001'), (106, '400000002'), (106, '400000003'), (106, '400000004'), (106, '400000005'), (106, '400000006'),
(107, '400000007'), (107, '400000008'), (107, '400000009'), (107, '400000010'), (107, '400000011'), (107, '400000012');

-- =============================================
-- ORDERS & TICKETS
-- =============================================
-- Order 1: Nov 2025 (Completed)
INSERT INTO FlightOrder (order_id, customer_email, flight_id, order_date, order_status, total_payment) 
VALUES (1, 'c1@test.com', 101, '2025-11-01 10:00:00', 'Completed', 1000);
INSERT INTO Ticket (flight_id, order_id, plane_id, class_type, seat_number, price) 
VALUES (101, 1, 1, 'Business', '1A', 1000);

-- Order 2: Nov 2025 (Completed)
INSERT INTO FlightOrder (order_id, customer_email, flight_id, order_date, order_status, total_payment) 
VALUES (2, 'c2@test.com', 101, '2025-11-02 10:00:00', 'Completed', 500);
INSERT INTO Ticket (flight_id, order_id, plane_id, class_type, seat_number, price) 
VALUES (101, 2, 1, 'Economy', '10A', 500);

-- Order 3: Dec 2025 (Completed)
INSERT INTO FlightOrder (order_id, customer_email, flight_id, order_date, order_status, total_payment) 
VALUES (3, 'c3@test.com', 102, '2025-12-01 10:00:00', 'Completed', 900);
INSERT INTO Ticket (flight_id, order_id, plane_id, class_type, seat_number, price) 
VALUES (102, 3, 3, 'Business', '1A', 900);

-- Order 4: Dec 2025 (Canceled By Client)
INSERT INTO FlightOrder (order_id, customer_email, flight_id, order_date, order_status, total_payment) 
VALUES (4, 'c4@test.com', 102, '2025-12-05 10:00:00', 'Canceled_By_Client', 45.00); 
INSERT INTO Ticket (flight_id, order_id, plane_id, class_type, seat_number, price) 
VALUES (102, 4, 3, 'Economy', '12A', 900);

-- Order 5: Jan 2026 (Active)
INSERT INTO FlightOrder (order_id, customer_email, flight_id, order_date, order_status, total_payment) 
VALUES (5, 'c1@test.com', 103, '2026-01-10 10:00:00', 'Active', 200);
INSERT INTO Ticket (flight_id, order_id, plane_id, class_type, seat_number, price) 
VALUES (103, 5, 4, 'Economy', '1A', 200);

-- Order 6: Feb 2026 (Canceled By Company)
INSERT INTO FlightOrder (order_id, customer_email, flight_id, order_date, order_status, total_payment) 
VALUES (6, 'c2@test.com', 104, '2026-02-01 10:00:00', 'Canceled_By_Company', 0);
INSERT INTO Ticket (flight_id, order_id, plane_id, class_type, seat_number, price) 
VALUES (104, 6, 5, 'Economy', '1A', 300);

-- Order 7: Mar 2026 (Active)
INSERT INTO FlightOrder (order_id, customer_email, flight_id, order_date, order_status, total_payment) 
VALUES (7, 'c3@test.com', 105, '2026-03-01 10:00:00', 'Active', 600);
INSERT INTO Ticket (flight_id, order_id, plane_id, class_type, seat_number, price) 
VALUES (105, 7, 1, 'Economy', '10B', 600);

-- Order 8: Mar 2026 (Active)
INSERT INTO FlightOrder (order_id, customer_email, flight_id, order_date, order_status, total_payment) 
VALUES (8, 'c5@test.com', 105, '2026-03-02 10:00:00', 'Active', 1200);
INSERT INTO Ticket (flight_id, order_id, plane_id, class_type, seat_number, price) 
VALUES (105, 8, 1, 'Business', '1B', 1200);