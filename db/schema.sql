-- מנהל
CREATE TABLE Manager (
    id_number VARCHAR(9) PRIMARY KEY, -- תעודת זהות
    first_name_hebrew VARCHAR(50) NOT NULL, -- שם פרטי בעברית
    last_name_hebrew VARCHAR(50) NOT NULL, -- שם משפחה בעברית
    start_date DATE NOT NULL, -- תאריך תחילת עבודה
    phone_number VARCHAR(20) NOT NULL, -- טלפון
    city VARCHAR(50), -- עיר מגורים
    street VARCHAR(50), -- רחוב מגורים
    house_number VARCHAR(10), -- מספר בית
    account_password VARCHAR(255) NOT NULL -- סיסמה
);

-- טייס
CREATE TABLE Pilot (
    id_number VARCHAR(9) PRIMARY KEY, -- תעודת זהות
    first_name_hebrew VARCHAR(50) NOT NULL, -- שם פרטי בעברית
    last_name_hebrew VARCHAR(50) NOT NULL, -- שם משפחה בעברית
    start_date DATE NOT NULL, -- תאריך תחילת עבודה
    phone_number VARCHAR(20) NOT NULL, -- טלפון
    city VARCHAR(50), -- עיר מגורים
    street VARCHAR(50), -- רחוב מגורים
    house_number VARCHAR(10), -- מספר בית
    is_long_haul_qualified BOOLEAN NOT NULL DEFAULT FALSE -- הכשרה לטיסות ארוכות
);

-- דייל
CREATE TABLE FlightAttendant (
    id_number VARCHAR(9) PRIMARY KEY, -- תעודת זהות
    first_name_hebrew VARCHAR(50) NOT NULL, -- שם פרטי בעברית
    last_name_hebrew VARCHAR(50) NOT NULL, -- שם משפחה בעברית
    start_date DATE NOT NULL, -- תאריך תחילת עבודה
    phone_number VARCHAR(20) NOT NULL, -- טלפון
    city VARCHAR(50), -- עיר מגורים
    street VARCHAR(50), -- רחוב מגורים
    house_number VARCHAR(10), -- מספר בית
    is_long_haul_qualified BOOLEAN NOT NULL DEFAULT FALSE -- הכשרה לטיסות ארוכות
);

-- קו טיסה
CREATE TABLE FlightLine (
    origin_airport VARCHAR(50) NOT NULL, -- שדה מקור
    destination_airport VARCHAR(50) NOT NULL, -- שדה יעד
    flight_duration DECIMAL(4,2) NOT NULL, -- משך טיסה (בשעות)
    PRIMARY KEY (origin_airport, destination_airport)
);

-- מטוס
CREATE TABLE Plane (
    plane_id INT PRIMARY KEY, -- מזהה מטוס
    manufacturer ENUM('Boeing', 'Airbus', 'Dassault') NOT NULL, -- יצרן
    size_category ENUM('Large', 'Small') NOT NULL, -- גודל
    acquisition_date DATE NOT NULL -- תאריך רכישה
);

-- טיסה (תוקן - נוספו עמודות מחיר)
CREATE TABLE Flight (
    flight_id INT AUTO_INCREMENT PRIMARY KEY, -- מזהה טיסה
    origin_airport VARCHAR(50) NOT NULL,
    destination_airport VARCHAR(50) NOT NULL,
    plane_id INT NOT NULL, -- מזהה מטוס(F)
    departure_datetime DATETIME NOT NULL, -- תאריך ושעת המראה
    manager_id VARCHAR(9) NOT NULL, -- תעודת זהות
    status ENUM('Active', 'Full', 'Landed', 'Canceled') NOT NULL DEFAULT 'Active', -- סטטוס טיסה
    price_economy DECIMAL(10, 2) NOT NULL DEFAULT 800.00, -- מחיר מחלקה רגילה
    price_business DECIMAL(10, 2) DEFAULT NULL, -- מחיר מחלקה עסקים (NULL למטוס קטן)
    FOREIGN KEY (plane_id) REFERENCES Plane(plane_id),
    FOREIGN KEY (manager_id) REFERENCES Manager(id_number),
    FOREIGN KEY (origin_airport, destination_airport) 
        REFERENCES FlightLine(origin_airport, destination_airport)
);

-- מחלקה
CREATE TABLE PlaneClass (
    plane_id INT, -- מזהה מטוס(F)
    class_type ENUM('Economy', 'Business') NOT NULL, -- סוג מחלקה
    rows_count INT NOT NULL, -- מספר שורות
    cols_count INT NOT NULL, -- מספר טורים
    PRIMARY KEY (plane_id, class_type),
    FOREIGN KEY (plane_id) REFERENCES Plane(plane_id) ON DELETE CASCADE
);

-- מושב
CREATE TABLE Seat (
    plane_id INT, -- מזהה מטוס(F)
    class_type ENUM('Economy', 'Business'), -- סוג מחלקה(F)
    seat_number VARCHAR(10), -- מספר מושב
    PRIMARY KEY (plane_id, class_type, seat_number),
    FOREIGN KEY (plane_id, class_type) REFERENCES PlaneClass(plane_id, class_type) ON DELETE CASCADE
);

-- לקוח
CREATE TABLE Customer (
    email VARCHAR(100) PRIMARY KEY, -- כתובת מייל
    first_name_english VARCHAR(50) NOT NULL, -- שם פרטי באנגלית
    last_name_english VARCHAR(50) NOT NULL -- שם משפחה באנגלית
);

-- טלפון לקוחות
CREATE TABLE CustomerPhone (
    email VARCHAR(100), -- כתובת מייל(F)
    phone_number VARCHAR(20), -- מספר טלפון
    PRIMARY KEY (email, phone_number),
    FOREIGN KEY (email) REFERENCES Customer(email) ON DELETE CASCADE
);

-- לקוח רשום
CREATE TABLE RegisteredCustomer (
    email VARCHAR(100) PRIMARY KEY, -- כתובת מייל(F)
    registration_date DATE NOT NULL, -- תאריך הרשמה למערכת
    birth_date DATE NOT NULL, -- תאריך לידה
    passport_number VARCHAR(20) NOT NULL, -- מספר דרכון
    account_password VARCHAR(255) NOT NULL, -- סיסמה
    balance DECIMAL (10,2) DEFAULT 0,
    FOREIGN KEY (email) REFERENCES Customer(email) ON DELETE CASCADE
);

-- הזמנה
CREATE TABLE FlightOrder (
    order_id INT AUTO_INCREMENT PRIMARY KEY, -- קוד הזמנה
    customer_email VARCHAR(100) NOT NULL, -- כתובת מייל(F)
    flight_id INT NOT NULL, -- מזהה טיסה(F)
    order_date DATETIME NOT NULL, -- תאריך ביצוע הזמנה
    order_status ENUM('Active', 'Completed', 'Canceled_By_Client', 'Canceled_By_Company') NOT NULL, -- סטטוס הזמנה
    total_payment DECIMAL(10, 2) NOT NULL DEFAULT 0.00, -- סכום לתשלום
    FOREIGN KEY (customer_email) REFERENCES Customer(email),
    FOREIGN KEY (flight_id) REFERENCES Flight(flight_id)
);

-- כרטיס טיסה
CREATE TABLE Ticket (
    ticket_id INT AUTO_INCREMENT PRIMARY KEY,
    flight_id INT NOT NULL, -- מזהה טיסה
    order_id INT NOT NULL, -- קוד הזמנה(F)
    plane_id INT NOT NULL, -- מזהה מטוס(F)
    class_type ENUM('Economy', 'Business') NOT NULL, -- סוג מחלקה(F)
    seat_number VARCHAR(10) NOT NULL, -- מספר מושב(F)
    price DECIMAL(10, 2) NOT NULL, -- מחיר
    UNIQUE (flight_id, seat_number),
    FOREIGN KEY (flight_id) REFERENCES Flight(flight_id) ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES FlightOrder(order_id) ON DELETE CASCADE,
    FOREIGN KEY (plane_id, class_type, seat_number) 
        REFERENCES Seat(plane_id, class_type, seat_number)
);

-- שיבוץ טייסים בטיסה
CREATE TABLE FlightPilotAssignment (
    pilot_id VARCHAR(9), -- תעודת זהות טייס(F)
    flight_id INT, -- מזהה טיסה(F)
    PRIMARY KEY (pilot_id, flight_id),
    FOREIGN KEY (pilot_id) REFERENCES Pilot(id_number),
    FOREIGN KEY (flight_id) REFERENCES Flight(flight_id)
);

-- שיבוץ דיילים בטיסה
CREATE TABLE FlightAttendantAssignment (
    flight_attendant_id VARCHAR(9), -- תעודת זהות דייל(F)
    flight_id INT, -- מזהה טיסה(F)
    PRIMARY KEY (flight_attendant_id, flight_id),
    FOREIGN KEY (flight_attendant_id) REFERENCES FlightAttendant(id_number),
    FOREIGN KEY (flight_id) REFERENCES Flight(flight_id)
);