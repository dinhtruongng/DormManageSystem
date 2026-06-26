# Design Pattern Conventions

Design patterns are reusable solutions to common software design problems. They should be used to improve maintainability, reduce duplicated logic, and make the system easier to extend.

Do **not** add design patterns just to make the report look advanced. A design pattern should solve a real problem in the system.

---

## 1. Purpose of Design Patterns

Design patterns help developers:

* Reuse proven design solutions.
* Reduce tightly coupled code.
* Improve code readability and maintainability.
* Separate responsibilities between classes.
* Make the system easier to modify and extend.
* Communicate design decisions clearly.

---

## 2. Main Types of Design Patterns

| Type                | Purpose                                | Examples                           |
| ------------------- | -------------------------------------- | ---------------------------------- |
| Creational patterns | Control object creation                | Singleton, Factory Method, Builder |
| Structural patterns | Organize relationships between classes | Adapter, Facade, Decorator         |
| Behavioral patterns | Manage communication and behavior      | Observer, Strategy, Command        |

---

## 3. Recommended Documentation Format

For each design pattern used in the report, describe it using this structure:

```text
Pattern Name:
Problem:
Reason for Use:
Classes Involved:
How It Works:
Benefit:
```

Example:

```text
Pattern Name: Repository Pattern
Problem: Database access logic is mixed with business logic.
Reason for Use: To separate data access from services.
Classes Involved: StudentRepository, RoomRepository, PaymentRepository
How It Works: Service classes call repositories instead of directly querying the database.
Benefit: Easier maintenance, testing, and database replacement.
```

---

## 4. Recommended Patterns for Student Dorm Management System

| Pattern        | Where to Use              | Purpose                                                           |
| -------------- | ------------------------- | ----------------------------------------------------------------- |
| Repository     | Data access layer         | Separate database logic from business logic                       |
| Service Layer  | Business logic layer      | Keep controllers simple                                           |
| MVC            | Web application structure | Separate model, view, and controller                              |
| Factory Method | Object creation           | Create different user/account types                               |
| Singleton      | Shared configuration      | Manage one shared database/config instance                        |
| Strategy       | Payment processing        | Support multiple payment methods                                  |
| Observer       | Notifications             | Notify students about payments, contracts, or maintenance updates |
| Facade         | Complex subsystem access  | Provide simple APIs for complex operations                        |

---

## 5. Example Pattern Usage

### Repository Pattern

```text
Controller → Service → Repository → Database
```

Example:

```text
StudentController
StudentService
StudentRepository
Student
```

Purpose:

```text
The controller handles HTTP requests.
The service handles business rules.
The repository handles database operations.
```

---

### Service Layer Pattern

```text
RoomController → RoomService → RoomRepository
```

Example business rules in `RoomService`:

```text
- Check room capacity before assigning a student
- Prevent assignment to unavailable rooms
- Update room status when capacity is full
```

---

### Strategy Pattern

Use this when the system supports different payment methods.

```text
PaymentStrategy
├── CashPaymentStrategy
├── BankTransferPaymentStrategy
└── OnlinePaymentStrategy
```

Purpose:

```text
Each payment method has its own processing logic, but the PaymentService can use them through a common interface.
```

---

### Observer Pattern

Use this for notifications.

```text
PaymentService → NotificationService → Student
```

Example:

```text
When a payment is overdue, the system sends a notification to the student.
```

---

## 6. When to Use Design Patterns

Use a design pattern when:

```text
- The same design problem appears multiple times
- Business logic is becoming too complex
- Classes have too many responsibilities
- Code is difficult to test or modify
- The system needs to support future extensions
```

Avoid using a pattern when:

```text
- The problem is simple
- The pattern adds unnecessary complexity
- The team does not understand the pattern
- The pattern does not match the actual system design
```

---

## 7. Common Mistakes to Avoid

* Listing design patterns without explaining where they are used.
* Using too many patterns in a small project.
* Forcing a pattern into code that does not need it.
* Confusing architecture patterns with class-level design patterns.
* Saying “Singleton is used everywhere.”
* Mixing business logic directly inside controllers.
* Mixing database queries directly inside UI or controller classes.
* Using inheritance where composition would be simpler.

---

## 8. Summary

```text
Design pattern = reusable solution for a recurring design problem
```

Recommended convention for the report:

```text
- Name each pattern clearly
- Explain the problem it solves
- Identify the classes involved
- Explain how the pattern works in the system
- State the benefit of using it
- Only include patterns actually reflected in the code/design
```

For a Student Dorm Management System, the most practical patterns are:

```text
Repository
Service Layer
MVC
Strategy
Observer
Facade
```
