# TalentFlow

TalentFlow is a modern HR and talent management platform designed to streamline employee lifecycle management for startups and growing companies. It helps HR teams and managers manage employees, attendance, payroll, and compliance in one unified system.

This project was built as part of my full-stack journey, with a strong focus on designing scalable architecture, integrating third-party services, and deploying across modern cloud platforms.

---

## 🚀 Features

* **Employee Management**: Maintain employee records with unique employee IDs.
* **Attendance Tracking**: Record working hours, overtime, and late arrivals.
* **Payroll System**: Automated salary calculation with taxes, bonuses, and deductions.
* **Overtime & Lateness Handling**: Business rules to adjust payroll based on extra hours or delays.
* **Secure File Storage**: Integration with **Cloudinary** for documents and employee files.
* **Authentication**: Secure login and role-based access control.
* **Scalable Deployment**: Runs across multiple cloud services for reliability and flexibility.

---

## 🛠️ Tech Stack

* **Frontend**: React.js
* **Backend**: Django REST Framework
* **Database**: PostgreSQL
* **File Storage**: Cloudinary
* **Deployment**:

  * **Neon** → PostgreSQL database hosting
  * **Vercel** → Frontend deployment
  * **Railway (Docker)** → Backend deployment

---

## 📦 Installation & Setup

Clone the repository:

```bash
git clone https://github.com/momen186/talentflow.git
cd talentflow
```

### 🔹 Backend Setup (Django)

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Environment variables required (`.env`):

```
SECRET_KEY=your_secret_key
DEBUG=True
DATABASE_URL=postgresql://user:password@localhost:5432/talentflow
CLOUDINARY_URL=cloudinary://<api_key>:<api_secret>@<cloud_name>
```

### 🔹 Frontend Setup (React)

```bash
cd frontend
npm install
npm run dev
```

Environment variables required (`.env.local`):

```
VITE_API_URL=http://localhost:8000/api
```

---

## 🌍 Deployment Journey

TalentFlow wasn’t just about writing code—it was about **orchestrating a modern full-stack deployment**.

* The **backend** runs as a Dockerized service on **Railway**, ensuring scalability and isolated environments.
* The **frontend** is deployed on **Vercel** for fast, serverless delivery.
* The **PostgreSQL database** is hosted on **Neon**, providing cloud-native database performance.
* **Cloudinary** powers media storage, making it easy to manage employee files and contracts.

---

## 📡 API Endpoints

### Authentication

* `POST /api/auth/register` → Register a new user
* `POST /api/auth/login` → Login and receive JWT
* `GET /api/auth/profile` → Get authenticated user profile

### Employees

* `GET /api/employees/` → List all employees
* `POST /api/employees/` → Add a new employee
* `GET /api/employees/{id}/` → Get employee details
* `PUT /api/employees/{id}/` → Update employee record
* `DELETE /api/employees/{id}/` → Remove employee

### Attendance

* `GET /api/attendance/` → List attendance records
* `POST /api/attendance/` → Record attendance (check-in/check-out)
* `PUT /api/attendance/{id}/` → Update attendance entry (late, overtime, etc.)

### Payroll

* `GET /api/payroll/` → View payroll reports
* `POST /api/payroll/generate` → Generate payroll for a period
* Payroll processing includes: **base salary + overtime – lateness deductions – taxes + bonuses**

# TalentFlow Database Indexes

Based on the provided models, here are the database indexes explicitly declared and implicitly created by constraints:

---

## 📌 **accounts/models.py** → `CustomUser`

* `id` → Primary Key (UUID)
* `email` → **Unique index** (for authentication)

---

## 📌 **api/models.py**

### `Employee`

* `employee.id` → Primary Key
* `user_id` → Foreign Key to `CustomUser` (indexed automatically)
* Indexes defined:

  * `emp_date_joined_idx` → on `date_joined`
  * `emp_status_idx` → on `status`
  * `emp_dept_status_idx` → composite index on `(department, status)`
  * `emp_job_status_idx` → composite index on `(job_title, status)`

### `Department`

* `id` → Primary Key

### `JobTitle`

* `id` → Primary Key

### `LeaveNote`

* `id` → Primary Key
* `employee_id` → Foreign Key to `Employee` (indexed automatically)

### `Exit`

* `id` → Primary Key
* `employee_id` → Foreign Key to `Employee` (indexed automatically)
* Indexes defined via `Meta.ordering`:

  * implicit index on `exit_date`
  * implicit index on `created_at`

---

## 📌 **attendance/models.py** → `Attendance`

* `id` → Primary Key
* `employee_id` → Foreign Key to `Employee` (indexed automatically)
* Unique constraint: `(employee, date)` → creates composite **unique index**
* Indexes defined:

  * `attendance_date_idx` → on `date`
  * `attendance_employee_idx` → on `employee`

---

## 📌 **hr/models.py**

### `PayRoll`

* `id` → Primary Key
* `employee_id` → Foreign Key to `Employee` (indexed automatically)
* Unique constraint: `(employee, year, month)` → creates composite **unique index**
* Indexes defined:

  * `payroll_year_month_idx` → on `(-year, -month)` (Django translates ordering indexes)
  * `payroll_employee_idx` → on `employee`

### `CompanyPolicy`

* `id` → Primary Key

---

# ✅ Summary of Important Indexes

* **Employees**: indexed by `status`, `date_joined`, `(department, status)`, `(job_title, status)`
* **Attendance**: composite unique `(employee, date)` + individual indexes on `employee` and `date`
* **Payroll**: composite unique `(employee, year, month)` + indexes on `(year, month)` and `employee`
* **Foreign keys** automatically create indexes (e.g., `employee_id` in multiple tables)
* **User emails** are indexed uniquely for authentication.

---

This schema is already well-optimized for:

* Filtering employees by **status**, **department**, or **job title**
* Fetching attendance by **employee and date**
* Running payroll reports by **employee and month/year**


## 📊 System Workflow

### Attendance & Overtime Handling

1. Employees check-in and check-out via the system.
2. Attendance logs calculate total hours, late minutes, and overtime hours.
3. Overtime is added to payroll, late arrivals are deducted.

### Payroll Processing

1. Payroll is generated monthly/periodically.
2. Salary = Base Salary + Overtime – Lateness Deductions – Taxes + Bonuses.
3. Detailed reports are generated for compliance and audits.

---

## 📐 ERD (Entity Relationship Diagram)

![ERD](./graphviz%20(1).svg)
---

## 🏗️ System Architecture

![Alt text](./full%20system%20architecture.png)
---


⚙️ Business Logic

Attendance Tracking

Each employee can have only one attendance record per day (enforced by unique index (employee, date)).

Late arrivals are calculated against a fixed company start time (default: 9:00 AM).

Overtime is calculated when check-out is later than company end time (default: 5:00 PM).

Payroll Processing

Payroll entries are unique per employee per month (employee, year, month).

Gross Pay = Base Compensation + Bonus.

Net Pay = Gross Pay – Taxes – Deductions.

Late arrivals and absences are deducted according to CompanyPolicy.

Overtime is rewarded according to CompanyPolicy.

Leave & Exit Management

Employees can submit leave notes, which must be approved or denied by HR.

Exit records cannot have an exit_date earlier than the date_joined of the employee.

All exits must have an associated type: voluntary, involuntary, or end of contract.

Security & Integrity

Foreign keys are protected or cascaded to maintain referential integrity:

Attendance and payroll are tied to employees.

Employee exits and leave notes are tied to employee records.

CustomUser email is unique and serves as the login credential.

🗂️ Business Logic Diagram

To visualize workflows like attendance handling, payroll calculation, and leave/exit management, include a diagram:

![Business Logic Diagram](business%20logic%20for%20talent%20flow.png)

(Placeholder: replace with actual diagram once created)


## 📈 Achievements

* Built a **production-ready HR & payroll management system** from scratch.
* Implemented **attendance-based payroll automation** with tax and overtime handling.
* Applied **database indexing** for performance optimization.
* Successfully integrated **multi-cloud deployment** (Neon, Vercel, Railway) with Docker.

---

## 👤 Author

**Momen Ehab**

* Software Engineer | Full-Stack Developer
* [GitHub](https://github.com/momen186)
