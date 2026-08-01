# TrekConnect – Trekking Management System

TrekConnect is a web-based trekking management application developed as part of the **IIT Madras BS Degree – Modern Application Development II** project.

The application provides a centralized platform for managing trekking events, staff members, trekker registrations, bookings, attendance, and trek reports.

The system supports three different user roles:

- Admin
- Staff
- User / Trekker

Each role has separate permissions and functionality.

---

# 1. Project Overview

Managing trekking events involves several activities such as creating treks, assigning staff, handling participant registrations, maintaining attendance, and tracking trek completion.

TrekConnect simplifies these activities through a role-based web application.

The application allows administrators to manage the complete trekking system, staff members to manage their assigned treks and participants, and users to discover and book available treks.

---

# 2. Technology Stack

The project is developed using the following technologies:

## Backend

- Python
- Flask
- Flask-SQLAlchemy
- Flask-Login
- SQLite

## Frontend

- HTML5
- CSS3
- Bootstrap 5
- Jinja2

## Development Tools

- Visual Studio Code
- Git
- GitHub

---

# 3. User Roles

## Admin

The administrator manages the overall TrekConnect system.

Admin functionality includes:

- Admin login
- View admin dashboard
- View system statistics
- Manage staff accounts
- Approve staff registrations
- Revoke staff approval
- Block staff
- Unblock staff
- Manage registered users
- Create treks
- Edit treks
- Delete treks
- Open trek registration
- Close trek registration
- Assign staff to treks
- Change assigned staff
- Remove assigned staff
- View all bookings
- Search bookings
- Filter bookings
- Search treks
- Filter treks
- View attendance information
- View system reports

---

## Staff

Staff members are responsible for managing the treks assigned to them.

A staff account must first be approved by the administrator before the staff member can access staff functionality.

Staff functionality includes:

- Staff login
- View staff dashboard
- View assigned treks
- View participants of assigned treks
- Mark participants as Present
- Mark participants as Absent
- Update attendance
- Mark a trek as Completed

A staff member can manage only the treks assigned to that staff account.

---

## User / Trekker

Registered users can explore and participate in available treks.

User functionality includes:

- User registration
- User login
- View user dashboard
- Browse available treks
- Search available treks
- Filter treks by difficulty
- Book a trek
- Prevent duplicate active bookings
- View booking history
- Cancel a booking
- View booking status

---

# 4. Authentication and Authorization

TrekConnect uses **Flask-Login** for authentication.

The system supports role-based authorization for:

- Admin
- Staff
- User

Protected routes can only be accessed by authenticated users with the appropriate role.

For example:

- Admin routes can only be accessed by administrators.
- Staff routes can only be accessed by approved staff.
- User routes can only be accessed by registered trekkers.

Blocked users and unapproved staff members are prevented from accessing protected functionality.

---

# 5. Trek Management

Administrators can create and manage trekking events.

Each trek contains information such as:

- Trek name
- Location
- Description
- Difficulty
- Duration
- Maximum slots
- Available slots
- Start date
- End date
- Registration status
- Assigned staff

Supported difficulty levels include:

- Easy
- Moderate
- Hard

A trek can have statuses such as:

- Open
- Closed
- Completed

---

# 6. Staff Assignment

An administrator can assign an approved staff member to a trek.

Each trek can have one assigned staff member.

The administrator can:

- Assign staff
- Change assigned staff
- Remove staff

Once assigned, the trek appears in the staff member's **Assigned Treks** section.

The staff member can then view the participants registered for that trek.

---

# 7. Trek Booking System

Users can book treks that satisfy the following conditions:

- Trek registration is Open
- Trek has available slots
- Trek is upcoming
- User does not already have an active booking for the trek

When a booking is successfully created:

- A booking record is stored.
- The available slot count decreases.

The system prevents duplicate active bookings for the same user and trek.

---

# 8. Booking Cancellation

Users can cancel eligible bookings.

When a booking is cancelled:

- Booking status changes to Cancelled.
- One slot is restored to the trek.

Cancelled bookings remain visible in the user's booking history.

This allows the application to maintain booking records instead of deleting booking history.

---

# 9. Attendance Management

Attendance is managed by the staff member assigned to a trek.

Every booking contains an attendance status.

Possible attendance values are:

- Pending
- Present
- Absent

The default attendance status is:

`Pending`

Assigned staff can change the attendance status to:

`Present`

or:

`Absent`

The administrator can view attendance information through Booking Management and Reports.

---

# 10. Trek Completion

Assigned staff members can mark their trek as Completed.

A trek cannot be marked as Completed while confirmed participants still have:

`Pending`

attendance.

Therefore, attendance must first be recorded for the participants.

Once all required attendance has been recorded, the assigned staff member can complete the trek.

This helps maintain consistent trek and attendance records.

---

# 11. Booking Management

The administrator can view bookings through the Booking Management page.

The page displays information such as:

- Booking ID
- Trekker name
- Trekker email
- Trek
- Trek date
- Booking date
- Booking status
- Attendance status

The administrator can also search and filter bookings.

---

# 12. Search and Filter System

TrekConnect provides search and filtering functionality in multiple sections.

## Admin Trek Management

Administrators can:

- Search by trek name
- Search by location
- Filter by difficulty
- Filter by trek status

Difficulty filters:

- Easy
- Moderate
- Hard

Status filters:

- Open
- Closed
- Completed

---

## Admin Booking Management

Administrators can search bookings using information such as:

- Trekker name
- Email
- Trek name
- Trek location

Bookings can also be filtered by:

### Booking Status

- Confirmed
- Cancelled

### Attendance

- Pending
- Present
- Absent

Search and filters can be used together.

---

## User Available Treks

Users can:

- Search by trek name
- Search by location
- Filter by difficulty

Only available, upcoming and open treks with available slots are shown to users.

---

# 13. Reports

The administrator has access to a Reports section.

The reports provide system statistics such as:

## Trek Statistics

- Total Treks
- Open Treks
- Closed Treks
- Completed Treks

## Booking Statistics

- Confirmed Bookings
- Cancelled Bookings

## Attendance Statistics

- Present
- Absent
- Attendance Pending

The application also provides a trek-wise report containing:

- Trek
- Location
- Start Date
- Status
- Confirmed Participants
- Present Participants
- Absent Participants
- Pending Attendance

---

# 14. Database Models

The application primarily uses three database models:

## User

The User model stores information about administrators, staff members and trekkers.

Important fields include:

- id
- name
- email
- password
- contact
- role
- is_approved
- is_blacklisted

---

## Trek

The Trek model stores trekking event information.

Important fields include:

- id
- name
- location
- description
- difficulty
- duration
- maximum_slots
- available_slots
- start_date
- end_date
- status
- assigned_staff_id

`assigned_staff_id` connects a trek with the staff member assigned to manage it.

---

## Booking

The Booking model connects a user with a trek.

Important fields include:

- id
- user_id
- trek_id
- booking_date
- status
- attendance_status

The combination of user and trek is constrained to prevent duplicate booking records for the same user and trek.

---

# 15. Database Relationships

The main relationships in the system are:

```text
User
 |
 | books
 |
 v
Booking
 |
 | belongs to
 |
 v
Trek
```

Staff assignment follows:

```text
Staff
 |
 | assigned to
 |
 v
Trek
```

A user can have multiple bookings.

A trek can have multiple bookings.

A staff member can be assigned to multiple treks.

Each trek can have one assigned staff member.

---

# 16. Application Workflow

The general TrekConnect workflow is:

```text
Admin
  |
  | Creates Trek
  |
  v
Trek Created
  |
  | Assigns Staff
  |
  v
Staff Assigned
  |
  | User views available treks
  |
  v
User Books Trek
  |
  | Available slots decrease
  |
  v
Booking Confirmed
  |
  | Assigned Staff views participants
  |
  v
Attendance Management
  |
  | Mark Present / Absent
  |
  v
Attendance Completed
  |
  | Staff completes trek
  |
  v
Trek Completed
  |
  v
Admin Reports Updated
```

---

# 17. Project Structure

A simplified project structure is:

```text
trekking-management-system/
│
├── app.py
├── models.py
├── update_db.py
├── README.md
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   └── videos/
│       ├── login.mp4
│       └── register.mp4
│
├── templates/
│   │
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   │
│   ├── admin/
│   │   ├── dashboard.html
│   │   ├── staff_management.html
│   │   ├── user_management.html
│   │   ├── trek_management.html
│   │   ├── add_trek.html
│   │   ├── edit_trek.html
│   │   ├── assign_staff.html
│   │   ├── booking_management.html
│   │   └── reports.html
│   │
│   ├── staff/
│   │   ├── dashboard.html
│   │   ├── assigned_treks.html
│   │   └── participants.html
│   │
│   └── user/
│       ├── dashboard.html
│       ├── available_treks.html
│       └── my_bookings.html
│
└── instance/
    └── trekconnect.db
```

The exact generated database location may depend on the local Flask configuration.

---

# 18. Installation

Clone the repository:

```bash
git clone <repository-url>
```

Move into the project directory:

```bash
cd trekking-management-system
```

Create a virtual environment:

### Windows

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

Install the required Python packages.

Example:

```bash
pip install flask flask-sqlalchemy flask-login werkzeug
```

---

# 19. Running the Application

Start the Flask application using:

```bash
python app.py
```

The application will normally run at:

```text
http://127.0.0.1:5000
```

Open the address in a web browser.

---

# 20. Default Administrator

The application creates a default administrator account when required by the project setup.

For security reasons, production applications should not store default credentials directly in source code.

For demonstration or evaluation, use the administrator credentials configured in the local project.

---

# 21. Important Business Rules

TrekConnect follows several important rules:

1. Only approved staff can access staff functionality.
2. Blocked accounts cannot access protected functionality.
3. Only administrators can manage staff and users.
4. Only administrators can create, edit or delete treks.
5. Only administrators can assign staff to treks.
6. Users can only book open and available treks.
7. Duplicate active trek bookings are prevented.
8. Cancelling a booking restores an available slot.
9. Only the assigned staff member can manage participants for a trek.
10. Attendance begins as Pending.
11. Staff can mark participants Present or Absent.
12. A trek cannot be completed while required attendance is still Pending.
13. Administrators can monitor bookings and attendance through reports.

---

# 22. Key Features

The main features of TrekConnect are:

- Role-based authentication
- Admin dashboard
- Staff dashboard
- User dashboard
- Staff approval system
- User management
- Trek CRUD operations
- Trek registration control
- Staff assignment
- Trek booking
- Duplicate booking prevention
- Booking cancellation
- Automatic slot management
- Participant management
- Attendance management
- Trek completion
- Booking management
- Reports
- Search functionality
- Multiple filters
- Responsive Bootstrap interface
- Trekking-themed landing page
- Video-based authentication pages

---

# 23. Future Improvements

Possible future improvements include:

- Trek images
- Online payment integration
- Email booking confirmations
- Trek ratings and reviews
- Weather information
- Trek maps
- Emergency contact management
- Certificate generation
- Advanced analytics
- Pagination for large datasets

---

# 24. Conclusion

TrekConnect provides a complete role-based trekking management workflow connecting administrators, staff members and trekkers.

The system manages the complete lifecycle of a trekking event, beginning with trek creation and staff assignment, followed by user booking and attendance management, and finally trek completion and administrative reporting.

The project demonstrates the use of Flask, SQLAlchemy, SQLite, Flask-Login, Jinja2 and Bootstrap to develop a structured database-driven web application.