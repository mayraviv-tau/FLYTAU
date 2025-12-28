# FLYTAU API Documentation

REST API documentation for the FLYTAU flight booking system.

## Base URL

```
http://localhost:5000/api
```

## Authentication

The API uses session-based authentication. After login, a session cookie is set and must be included in subsequent requests.

---

## Authentication Endpoints

### Register Customer

Create a new customer account.

**Endpoint:** `POST /api/auth/register`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "birth_date": "1990-01-15",
  "passport_number": "A12345678",
  "phone_numbers": ["050-1234567"]
}
```

**Response:** `201 Created`
```json
{
  "success": true,
  "message": "Customer registered successfully",
  "data": {
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "balance": 0.0,
    "is_registered": true
  }
}
```

### Login

Login as a customer or manager.

**Endpoint:** `POST /api/auth/login`

**Request Body (Customer):**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "user_type": "customer"
}
```

**Request Body (Manager):**
```json
{
  "email": "200000001",
  "password": "manager123",
  "user_type": "manager"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user_id": "user@example.com",
    "user_type": "customer",
    "first_name": "John",
    "last_name": "Doe",
    "is_registered": true
  }
}
```

### Logout

Logout current user.

**Endpoint:** `POST /api/auth/logout`

**Authentication:** Required

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Logout successful"
}
```

### Get Current User

Get current user information.

**Endpoint:** `GET /api/auth/me`

**Authentication:** Required

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "user_type": "customer",
    "is_registered": true,
    "balance": 1500.0
  }
}
```

---

## Flight Endpoints

### Search Flights

Search for available flights.

**Endpoint:** `GET /api/flights`

**Query Parameters:**
- `date` (optional): Filter by departure date (YYYY-MM-DD)
- `origin` (optional): Filter by origin airport code
- `destination` (optional): Filter by destination airport code

**Example:** `GET /api/flights?origin=TLV&destination=JFK&date=2026-04-01`

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Found 2 flight(s)",
  "data": {
    "flights": [
      {
        "flight_id": 1,
        "origin_airport": "TLV",
        "destination_airport": "JFK",
        "departure_datetime": "2026-04-01 08:00:00",
        "flight_duration": 12.5,
        "status": "Active",
        "plane_id": 1,
        "manufacturer": "Boeing",
        "size_category": "Large",
        "available_seats": {
          "Business": 18,
          "Economy": 175
        }
      }
    ]
  }
}
```

### Get Flight Details

Get detailed flight information including seat map.

**Endpoint:** `GET /api/flights/{flight_id}`

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "flight_id": 1,
    "origin_airport": "TLV",
    "destination_airport": "JFK",
    "departure_datetime": "2026-04-01 08:00:00",
    "status": "Active",
    "seat_map": {
      "Business": {
        "total": 20,
        "available": ["1B", "1C", "2A"],
        "occupied": ["1A", "2B"]
      },
      "Economy": {
        "total": 180,
        "available": ["10B", "10C"],
        "occupied": ["10A"]
      }
    }
  }
}
```

---

## Booking & Order Endpoints

### Create Booking

Create a new flight booking.

**Endpoint:** `POST /api/bookings`

**Authentication:** Required (Customer only)

**Request Body:**
```json
{
  "flight_id": 1,
  "tickets": [
    {
      "class_type": "Business",
      "seat_number": "1A",
      "price": 1500.00
    },
    {
      "class_type": "Economy",
      "seat_number": "10A",
      "price": 800.00
    }
  ]
}
```

**Response:** `201 Created`
```json
{
  "success": true,
  "message": "Booking created successfully",
  "data": {
    "order_id": 5,
    "customer_email": "user@example.com",
    "flight_id": 1,
    "order_date": "2025-12-28 10:30:00",
    "order_status": "Active",
    "total_payment": 2300.00,
    "flight": {
      "origin_airport": "TLV",
      "destination_airport": "JFK",
      "departure_datetime": "2026-04-01 08:00:00"
    },
    "tickets": [
      {
        "class_type": "Business",
        "seat_number": "1A",
        "price": 1500.00
      }
    ]
  }
}
```

### Get Orders

Get user's orders.

**Endpoint:** `GET /api/orders`

**Authentication:** Required (Customer only)

**Query Parameters:**
- `filter` (optional): "future" or "history"

**Example:** `GET /api/orders?filter=future`

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Found 2 order(s)",
  "data": {
    "orders": [
      {
        "order_id": 5,
        "customer_email": "user@example.com",
        "flight_id": 1,
        "order_date": "2025-12-28 10:30:00",
        "order_status": "Active",
        "total_payment": 2300.00,
        "flight": {
          "origin_airport": "TLV",
          "destination_airport": "JFK",
          "departure_datetime": "2026-04-01 08:00:00",
          "status": "Active"
        },
        "tickets": [...]
      }
    ]
  }
}
```

### Get Order Details

Get specific order details.

**Endpoint:** `GET /api/orders/{order_id}`

**Authentication:** Required

**Response:** `200 OK`

### Cancel Order

Cancel an order.

**Endpoint:** `DELETE /api/orders/{order_id}`

**Authentication:** Required (Customer only, must own order)

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Order canceled successfully",
  "data": {
    "order_id": 5,
    "status": "Canceled_By_Client",
    "original_payment": 2300.00,
    "cancellation_fee": 115.00,
    "refund_amount": 2185.00,
    "refunded_to_balance": true
  }
}
```

---

## Admin Flight Management

### Create Flight

Create a new flight.

**Endpoint:** `POST /api/admin/flights`

**Authentication:** Required (Manager only)

**Request Body:**
```json
{
  "origin_airport": "TLV",
  "destination_airport": "JFK",
  "plane_id": 1,
  "departure_datetime": "2026-05-01T10:00:00",
  "pilot_ids": ["300000001", "300000002", "300000003"],
  "attendant_ids": ["400000001", "400000002", "400000003", "400000004", "400000005", "400000006"]
}
```

**Response:** `201 Created`
```json
{
  "success": true,
  "message": "Flight created successfully",
  "data": {
    "flight_id": 10,
    "origin_airport": "TLV",
    "destination_airport": "JFK",
    "departure_datetime": "2026-05-01 10:00:00",
    "plane_id": 1,
    "status": "Active",
    "pilots_assigned": 3,
    "attendants_assigned": 6
  }
}
```

### Cancel Flight

Cancel a flight.

**Endpoint:** `DELETE /api/admin/flights/{flight_id}`

**Authentication:** Required (Manager only)

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Flight canceled successfully",
  "data": {
    "flight_id": 10,
    "status": "Canceled",
    "orders_canceled": 3,
    "total_refunded": 5000.00
  }
}
```

---

## Admin Reports

All report endpoints require manager authentication.

### Occupancy Report

Average flight occupancy percentage.

**Endpoint:** `GET /api/admin/reports/occupancy`

**Authentication:** Required (Manager only)

**Response:** `200 OK`

### Revenue Report

Revenue breakdown by plane size, manufacturer, and class.

**Endpoint:** `GET /api/admin/reports/revenue`

**Authentication:** Required (Manager only)

### Staff Hours Report

Accumulated flight hours for pilots and flight attendants.

**Endpoint:** `GET /api/admin/reports/staff-hours`

**Authentication:** Required (Manager only)

### Cancellation Rates Report

Monthly cancellation rates.

**Endpoint:** `GET /api/admin/reports/cancellations`

**Authentication:** Required (Manager only)

### Plane Activity Report

Monthly plane utilization metrics.

**Endpoint:** `GET /api/admin/reports/plane-activity`

**Authentication:** Required (Manager only)

---

## Error Responses

All errors follow this format:

```json
{
  "success": false,
  "error": "ErrorType",
  "message": "Detailed error message"
}
```

### Common Error Codes

- `400 Bad Request` - Validation error
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error
