# Business Logic Implementation Summary

## Overview

This document describes the critical business rule validations implemented for the FLYTAU flight booking system to ensure data integrity and enforce operational constraints.

## 1. Aircraft and Flight Compatibility Validation

### Implementation Location
- File: `app/ui/routes/manager.py` (lines 55-79)

### Rules Enforced
- **Small aircraft** can only be assigned to **short-haul flights** (≤ 6 hours)
- **Large aircraft** can handle both short and long-haul flights
- Flight duration is automatically retrieved from `FlightLine` table based on origin/destination
- Flight route must exist in `FlightLine` table

### How It Works
```python
# 1. Lookup flight duration from FlightLine
SELECT flight_duration FROM FlightLine
WHERE origin_airport = ? AND destination_airport = ?

# 2. Determine if long-haul (> 6 hours)
is_long_haul = flight_duration > 6

# 3. Validate aircraft size compatibility
IF plane.size_category == 'Small' AND is_long_haul:
    RAISE ERROR "Small aircraft cannot be assigned to long-haul flights"
```

### Error Messages
- `"No flight route exists from TLV to XYZ"` - Invalid route
- `"Small aircraft cannot be assigned to long-haul flights (>12.5h)"` - Size mismatch

## 2. Crew Requirements and Qualification Validation

### Implementation Location
- File: `app/ui/routes/manager.py` (lines 81-125)
- File: `app/ui/templates/manager/create_flight.html` (lines 55-59, 72-76)

### Rules Enforced

#### Crew Count Requirements
| Aircraft Size | Required Pilots | Required Attendants |
|--------------|----------------|---------------------|
| Large        | 3              | 6                   |
| Small        | 2              | 3                   |

#### Qualification Requirements
- **Long-haul flights** (> 6 hours):
  - Only crew with `is_long_haul_qualified = TRUE` can be assigned
  - Validates both pilots and flight attendants
- **Short-haul flights** (≤ 6 hours):
  - Any crew member can be assigned

### How It Works
```python
# 1. Determine required crew based on aircraft size
required_pilots = 3 if size == 'Large' else 2
required_attendants = 6 if size == 'Large' else 3

# 2. Validate crew count
IF selected_pilots < required_pilots:
    RAISE ERROR "Insufficient pilots: X/Y required"

# 3. For long-haul flights, check qualifications
IF is_long_haul:
    SELECT id_number FROM Pilot
    WHERE id_number IN (selected_pilots)
    AND is_long_haul_qualified = FALSE

    IF unqualified_pilots_found:
        RAISE ERROR "Pilots 300000006 are not qualified for long-haul flights"
```

### UI Enhancements
- Crew list now displays qualification status:
  - Long-haul (green checkmark) - Can fly long-haul routes
  - Short-haul only (orange warning) - Restricted to short flights

### Error Messages
- `"Insufficient pilots: 1/3 required for Large aircraft"`
- `"Insufficient flight attendants: 4/6 required for Large aircraft"`
- `"Pilots 300000006, 300000007 are not qualified for long-haul flights"`
- `"Flight attendants 400000010 are not qualified for long-haul flights"`

## 3. Flight Status Transitions

### Implementation Locations
- File: `app/server/services/booking_service.py` (lines 13-45, 114-115)

### Status Flow
```
Active → Full → Landed
   ↓       ↓       ↓
 [Can book] [Can book] [Cannot book]
```

### Automatic Transitions

#### To "Full" Status
- **Trigger**: When last available seat is booked
- **Location**: `booking_service.create_booking()` (line 114-115)
- **Logic**:
  ```python
  available_seats = get_available_seats(flight_id, plane_id)
  total_available = sum(available_seats.values())

  IF total_available == 0 AND status == 'Active':
      UPDATE Flight SET status = 'Full' WHERE flight_id = ?
  ```

#### To "Landed" Status
- **Trigger**: When current time ≥ (departure_datetime + flight_duration)
- **Function**: `update_completed_flights()` (new function, lines 13-45)
- **Logic**:
  ```python
  landing_time = departure_datetime + timedelta(hours=flight_duration)

  IF current_time >= landing_time:
      UPDATE Flight SET status = 'Landed' WHERE flight_id = ?
  ```

### Usage
The `update_completed_flights()` function should be called periodically by:
- A cron job (recommended every hour)
- A scheduler (e.g., APScheduler)
- Or manually via admin endpoint

**Example cron entry:**
```bash
0 * * * * cd /path/to/project && python3 -c "from app.server.services.booking_service import update_completed_flights; update_completed_flights()"
```

## 4. Role-Based Access Control

### Implementation Location
- File: `app/server/services/booking_service.py` (lines 64-66)
- File: `app/server/routes/orders.py` (lines 40-41, 67)

### Rules Enforced
- **Managers cannot purchase tickets** (HTTP 403 Forbidden)
- **Only customers** (registered or guest) can create bookings
- User type is validated at both route level and service level (defense in depth)

### How It Works

#### Route Level (First Layer)
```python
# In orders.py
current_user = get_current_user()

if current_user['user_type'] != 'customer':
    raise APIError("Only customers can create bookings", 403)
```

#### Service Level (Second Layer)
```python
# In booking_service.py
def create_booking(customer_email, flight_id, tickets, user_type='customer'):
    if user_type == 'manager':
        raise APIError("Managers are not authorized to purchase tickets", 403)
```

### Error Message
- `"Only customers can create bookings"` (route level)
- `"Managers are not authorized to purchase tickets"` (service level)

## Testing Examples

### Test 1: Small Aircraft on Long-Haul Route (Should Fail)
```http
POST /manager/flights/create
{
  "origin_airport": "TLV",
  "destination_airport": "JFK",  // 12.5 hour flight
  "plane_id": 4,                  // Small Airbus
  "pilot_ids": [...],
  "attendant_ids": [...]
}
```
**Expected**: Error: "Small aircraft cannot be assigned to long-haul flights (>12.5h)"

### Test 2: Insufficient Crew for Large Aircraft (Should Fail)
```http
POST /manager/flights/create
{
  "origin_airport": "TLV",
  "destination_airport": "LHR",
  "plane_id": 1,                  // Large Boeing (needs 3 pilots)
  "pilot_ids": ["300000001", "300000002"],  // Only 2 pilots
  "attendant_ids": [...]
}
```
**Expected**: Error: "Insufficient pilots: 2/3 required for Large aircraft"

### Test 3: Unqualified Crew on Long-Haul (Should Fail)
```http
POST /manager/flights/create
{
  "origin_airport": "TLV",
  "destination_airport": "JFK",  // Long-haul
  "plane_id": 1,
  "pilot_ids": ["300000006"],     // Not long-haul qualified
  ...
}
```
**Expected**: Error: "Pilots 300000006 are not qualified for long-haul flights"

### Test 4: Manager Attempts to Book Ticket (Should Fail)
```http
POST /api/bookings
Headers: {Session: manager_session}
{
  "flight_id": 1,
  "tickets": [...]
}
```
**Expected**: Error 403: "Only customers can create bookings"

### Test 5: Valid Flight Creation (Should Succeed)
```http
POST /manager/flights/create
{
  "origin_airport": "TLV",
  "destination_airport": "JFK",
  "plane_id": 1,                           // Large Boeing
  "pilot_ids": ["300000001", "300000002", "300000003"],  // 3 qualified pilots
  "attendant_ids": ["400000001", ...],     // 6 qualified attendants
  "departure_datetime": "2026-05-01 08:00:00"
}
```
**Expected**: Success: "Flight X created successfully! Duration: 12.5h (Long-haul)"

## Benefits

### Data Integrity
- Prevents invalid aircraft/route combinations
- Ensures adequate crew for safe operations
- Maintains crew qualification standards

### User Experience
- Clear, actionable error messages
- Visual indicators for crew qualifications
- Automatic status updates reduce manual work

### Compliance
- Enforces aviation safety regulations (crew counts, qualifications)
- Separates manager and customer roles
- Maintains audit trail of validation failures

## Future Enhancements (Optional)

1. **Crew Availability Checking**
   - Check for overlapping flight assignments
   - Implement crew scheduling calendar

2. **Dynamic Pricing**
   - Business class only available on large aircraft
   - Premium pricing for long-haul flights

3. **Automated Status Updates**
   - Set up cron job for `update_completed_flights()`
   - Real-time status dashboard for managers

4. **Enhanced Error Recovery**
   - Suggest alternative aircraft when validation fails
   - Show available qualified crew when selection invalid
