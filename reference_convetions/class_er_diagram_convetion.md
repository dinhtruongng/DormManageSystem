# Standard Conventions for Class Diagrams and ERDs

Use **one notation consistently**. Do not mix Chen ERD, Crow’s Foot ERD, UML class diagram, and database schema notation in the same diagram unless the report explicitly explains the mapping.

Class diagrams are mainly used for **software/object design**, while ERDs are used for **data/database design**.

---

## 1. UML Class Diagram Conventions

| Element               | Standard Convention                                                                 |
| --------------------- | ----------------------------------------------------------------------------------- |
| Class                 | Rectangle, usually with 3 compartments: **class name**, **attributes**, **methods** |
| Class name            | Singular noun, `PascalCase`: `Student`, `Room`, `Payment`                           |
| Attribute             | `visibility name: Type = defaultValue`                                              |
| Method                | `visibility methodName(param: Type): ReturnType`                                    |
| Visibility            | `+` public, `-` private, `#` protected, `~` package                                 |
| Abstract class/method | Italic text or `{abstract}`                                                         |
| Static member         | Underlined                                                                          |
| Interface             | `<<interface>>` or lollipop notation                                                |
| Enum                  | `<<enumeration>>`                                                                   |

Example:

```text
Room
--------------------------------
- roomId: int
- roomNumber: String
- capacity: int
- status: RoomStatus
--------------------------------
+ assignStudent(student: Student): void
+ isAvailable(): boolean
```

---

## 2. UML Relationship Conventions

| Relationship                 | Notation                         | Meaning                                |
| ---------------------------- | -------------------------------- | -------------------------------------- |
| Association                  | Solid line                       | General structural relationship        |
| Directed association         | Solid line with arrow            | Navigability                           |
| Aggregation                  | Hollow diamond                   | Weak whole-part relationship           |
| Composition                  | Filled diamond                   | Strong ownership; part dies with whole |
| Generalization / inheritance | Solid line with hollow triangle  | `Student` inherits from `User`         |
| Realization                  | Dashed line with hollow triangle | Class implements interface             |
| Dependency                   | Dashed arrow                     | Temporary usage/dependency             |

---

## 3. UML Multiplicity

Put multiplicity near each class end.

```text
1        exactly one
0..1     optional one
*        many
0..*     zero or many
1..*     one or many
m..n     bounded range
```

Example:

```text
Dormitory 1 ─── 0..* Room
Room 1 ─── 0..* Student
Student 1 ─── 0..* Payment
```

---

## 4. Practical Rules for Class Diagrams

Keep class diagrams about **software structure**, not raw database tables.

Recommended rules:

* Include domain classes such as `Student`, `Room`, `Contract`, and `Payment`.
* Include service/controller classes only when useful.
* Avoid showing every getter and setter unless required.
* Use private attributes and public operations by default.
* Use inheritance only for real **is-a** relationships.
* Use composition only when lifecycle ownership is strong.
* Avoid crossing lines.
* Split large diagrams into packages or modules.
* Show only relevant attributes and methods for the report.

---

## 5. ERD Conventions

| Element            | Standard Convention                                                                      |
| ------------------ | ---------------------------------------------------------------------------------------- |
| Entity             | Rectangle or table-like box                                                              |
| Entity name        | Singular noun: `Student`, `Room`, `Contract`                                             |
| Attribute          | Listed inside entity or attached as oval, depending on notation                          |
| Primary key        | Mark as `PK`, underline, or key icon                                                     |
| Foreign key        | Mark as `FK`                                                                             |
| Relationship       | Line between entities; relationship name should be a verb                                |
| Cardinality        | `1`, `0..1`, `1..*`, `0..*`, or Crow’s Foot symbols                                      |
| Weak entity        | Double rectangle in Chen notation, or dependency-identifying relationship in Crow’s Foot |
| Associative entity | Entity used to break many-to-many relationships                                          |

Example ERD style:

```text
STUDENT
- student_id PK
- full_name
- email
- phone

ROOM
- room_id PK
- room_number
- capacity
- status

CONTRACT
- contract_id PK
- student_id FK
- room_id FK
- start_date
- end_date
```

Relationship:

```text
Student 1 ─── 0..* Contract
Room    1 ─── 0..* Contract
```

This is better than a direct many-to-many relationship between `Student` and `Room`, because the `Contract` entity has its own attributes, such as:

* `start_date`
* `end_date`
* `status`

---

## 6. Class Diagram vs ERD

| Aspect             | Class Diagram                                                  | ERD                                       |
| ------------------ | -------------------------------------------------------------- | ----------------------------------------- |
| Purpose            | Software/object design                                         | Database/data design                      |
| Main unit          | Class                                                          | Entity/table                              |
| Contains behavior? | Yes, methods/operations                                        | No, usually data only                     |
| Relationships      | Association, inheritance, aggregation, composition, dependency | Primary key/foreign key relationships     |
| Used for           | Design model, implementation planning                          | Data requirements, database schema design |

---

## 7. Example for Student Dorm Management System

### Class Diagram Candidates

```text
User
Student
Admin
Room
Dormitory
Contract
Payment
MaintenanceRequest
NotificationService
```

### ERD Candidates

```text
users
students
admins
rooms
dormitories
contracts
payments
maintenance_requests
```

---

## 8. Recommended Convention for the Report

### Class Diagram

```text
- Use UML notation
- Use PascalCase class names
- Use private attributes and public methods
- Show multiplicity on associations
- Use inheritance only for real “is-a” relationships
- Use composition only when lifecycle ownership is strong
```

### ERD

```text
- Use Crow’s Foot notation
- Use singular entity names or consistent table names
- Mark PK and FK clearly
- Show cardinality and optionality
- Resolve many-to-many relationships using associative entities
- Keep attributes atomic and normalized
```

---

## 9. Common Mistakes to Avoid

* Drawing the ERD as if it were a class diagram.
* Adding methods to ERD entities.
* Adding raw database tables directly into the class diagram without object responsibilities.
* Omitting multiplicity/cardinality.
* Using inheritance where a foreign key relationship is more appropriate.
* Using composition when the part can exist independently.
* Leaving many-to-many relationships unresolved in the ERD.
* Mixing different diagram notations without explanation.

---

## 10. Summary

For a student project report, use this simple distinction:

```text
Class diagram = software objects + behavior + object relationships
ERD = database entities + attributes + PK/FK relationships
```

Use **UML class diagram notation** for the class diagram and **Crow’s Foot notation** for the ERD. This is clean, conventional, and appropriate for a software design and analysis report.

```
```
