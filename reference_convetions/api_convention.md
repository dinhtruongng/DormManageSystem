# API Design Conventions

Use **one API style consistently**. For a student project, **RESTful API design** is usually the safest and clearest choice.

API design defines how clients such as web apps, mobile apps, or external systems communicate with the backend.

---

## 1. API Design Goals

A good API should be:

* **Consistent**: similar endpoints follow the same structure.
* **Readable**: endpoint names clearly describe resources.
* **Predictable**: HTTP methods define the action.
* **Secure**: authentication and authorization are enforced.
* **Versioned**: API changes do not break existing clients.
* **Documented**: request, response, and errors are clearly described.

---

## 2. REST Endpoint Naming

Use **nouns**, not verbs.

Good:

```text
/api/v1/students
/api/v1/rooms
/api/v1/contracts
/api/v1/payments
/api/v1/maintenance-requests
```

Avoid:

```text
/api/v1/getStudents
/api/v1/createRoom
/api/v1/deletePayment
```

The HTTP method already describes the action.

---

## 3. HTTP Method Conventions

| Method   | Purpose               | Example                               |
| -------- | --------------------- | ------------------------------------- |
| `GET`    | Retrieve data         | `GET /api/v1/students`                |
| `POST`   | Create data           | `POST /api/v1/students`               |
| `PUT`    | Replace data          | `PUT /api/v1/students/{studentId}`    |
| `PATCH`  | Partially update data | `PATCH /api/v1/students/{studentId}`  |
| `DELETE` | Delete data           | `DELETE /api/v1/students/{studentId}` |

Example:

```text
GET    /api/v1/rooms
GET    /api/v1/rooms/{roomId}
POST   /api/v1/rooms
PATCH  /api/v1/rooms/{roomId}
DELETE /api/v1/rooms/{roomId}
```

---

## 4. Resource Naming Rules

Recommended rules:

```text
- Use plural nouns for collections
- Use kebab-case for multi-word resources
- Use camelCase for JSON fields
- Use clear path parameter names
- Avoid exposing database table names
```

Good:

```text
/api/v1/maintenance-requests
/api/v1/room-assignments
```

Avoid:

```text
/api/v1/tbl_student
/api/v1/student_table
/api/v1/MaintenanceRequest
```

---

## 5. URL Structure

Use this structure:

```text
/api/{version}/{resource}
/api/{version}/{resource}/{resourceId}
/api/{version}/{resource}/{resourceId}/{subResource}
```

Examples:

```text
/api/v1/students
/api/v1/students/{studentId}
/api/v1/students/{studentId}/contracts
/api/v1/rooms/{roomId}/maintenance-requests
```

Avoid overly deep nesting. Prefer query parameters when filtering:

```text
GET /api/v1/payments?studentId={studentId}
GET /api/v1/rooms?status=available
```

---

## 6. Query Parameters

Use query parameters for filtering, searching, sorting, and pagination.

```text
GET /api/v1/students?search=nguyen
GET /api/v1/rooms?status=available
GET /api/v1/payments?sort=-createdAt
GET /api/v1/students?page=1&limit=20
```

---

## 7. Request and Response Format

Use JSON for request and response bodies.

Example request:

```json
{
  "fullName": "Nguyen Van A",
  "email": "nguyenvana@example.com",
  "phone": "0901234567"
}
```

Example success response:

```json
{
  "success": true,
  "message": "Student created successfully.",
  "data": {
    "studentId": 1,
    "fullName": "Nguyen Van A",
    "email": "nguyenvana@example.com"
  }
}
```

Example error response:

```json
{
  "success": false,
  "message": "Validation failed.",
  "errors": [
    {
      "field": "email",
      "message": "Email is already in use."
    }
  ]
}
```

---

## 8. HTTP Status Codes

| Status Code                 | Meaning                 |
| --------------------------- | ----------------------- |
| `200 OK`                    | Request successful      |
| `201 Created`               | Resource created        |
| `204 No Content`            | Successful delete       |
| `400 Bad Request`           | Invalid request         |
| `401 Unauthorized`          | User is not logged in   |
| `403 Forbidden`             | User has no permission  |
| `404 Not Found`             | Resource does not exist |
| `409 Conflict`              | Business rule conflict  |
| `422 Unprocessable Entity`  | Validation error        |
| `500 Internal Server Error` | Server error            |

Example:

```text
POST /api/v1/contracts
```

Return `409 Conflict` if the selected room is already full.

---

## 9. Authentication and Authorization

Use token-based authentication:

```text
Authorization: Bearer <accessToken>
```

Recommended role-based access:

| Role      | Permissions                                       |
| --------- | ------------------------------------------------- |
| `Admin`   | Manage users, rooms, contracts, payments, reports |
| `Staff`   | Manage rooms, contracts, maintenance requests     |
| `Student` | View own profile, contract, payments, requests    |

Example:

```text
Admin:
GET /api/v1/students

Student:
GET /api/v1/students/me
```

Students should not access another student’s private data.

---

## 10. Validation Rules

Validate all input on the backend.

Examples:

```text
- email must be valid
- phone must match the expected format
- room capacity must be greater than 0
- contract startDate must be before endDate
- payment amount must be greater than 0
- room assignment must not exceed room capacity
```

---

## 11. API Versioning

Use versioned URLs:

```text
/api/v1/students
/api/v1/rooms
/api/v1/contracts
```

Avoid:

```text
/api/students
```

Versioning helps prevent breaking existing clients when the API changes.

---

## 12. Example APIs for Student Dorm Management System

### Students

```text
GET    /api/v1/students
GET    /api/v1/students/{studentId}
POST   /api/v1/students
PATCH  /api/v1/students/{studentId}
DELETE /api/v1/students/{studentId}
GET    /api/v1/students/{studentId}/contracts
GET    /api/v1/students/{studentId}/payments
```

### Rooms

```text
GET    /api/v1/rooms
GET    /api/v1/rooms/{roomId}
POST   /api/v1/rooms
PATCH  /api/v1/rooms/{roomId}
DELETE /api/v1/rooms/{roomId}
GET    /api/v1/rooms?status=available
```

### Contracts

```text
GET    /api/v1/contracts
GET    /api/v1/contracts/{contractId}
POST   /api/v1/contracts
PATCH  /api/v1/contracts/{contractId}
POST   /api/v1/contracts/{contractId}/terminate
```

### Payments

```text
GET    /api/v1/payments
GET    /api/v1/payments/{paymentId}
POST   /api/v1/payments
PATCH  /api/v1/payments/{paymentId}
POST   /api/v1/payments/{paymentId}/confirm
```

### Maintenance Requests

```text
GET    /api/v1/maintenance-requests
GET    /api/v1/maintenance-requests/{requestId}
POST   /api/v1/maintenance-requests
PATCH  /api/v1/maintenance-requests/{requestId}
POST   /api/v1/maintenance-requests/{requestId}/assign
POST   /api/v1/maintenance-requests/{requestId}/resolve
```

---

## 13. API Documentation Template

Use this format for each endpoint:

```text
Endpoint:
HTTP Method:
Description:
Required Role:
Path Parameters:
Query Parameters:
Request Body:
Success Response:
Error Responses:
Business Rules:
```

Example:

```text
Endpoint: /api/v1/rooms/{roomId}
HTTP Method: GET
Description: Retrieve room details.
Required Role: Admin, Staff, Student
Path Parameters:
- roomId: ID of the room

Success Response:
- 200 OK

Error Responses:
- 404 Not Found: Room does not exist
- 401 Unauthorized: User is not authenticated
```

---

## 14. Common Mistakes to Avoid

* Using verbs in endpoint names, such as `/getStudents`.
* Using `POST` for every operation.
* Returning inconsistent response formats.
* Ignoring HTTP status codes.
* Exposing database table names.
* Exposing passwords or sensitive tokens.
* Forgetting input validation.
* Forgetting authorization checks.
* Creating overly nested URLs.
* Omitting pagination for list endpoints.

---

## 15. Summary

```text
API design = external interface of the backend system
Class diagram = internal object/software structure
ERD = database/data structure
```

Recommended API convention:

```text
- Use RESTful API design
- Use plural resource names
- Use correct HTTP methods
- Use JSON request and response bodies
- Use consistent response format
- Use proper HTTP status codes
- Use /api/v1 for versioning
- Use authentication and role-based authorization
- Document request body, response body, errors, and business rules
```
