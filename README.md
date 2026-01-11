# SeatLock API 

A high-concurrency cinema booking backend designed to solve the "Double Booking" problem.
Unlike standard CRUD applications, this system uses database-level locking and asynchronous processing to ensure data integrity when multiple users attempt to book the same seat simultaneously.

##  Tech Stack

- **Core**: Python 3.10+, Django 5, Django REST Framework (DRF)
- **Database**: PostgreSQL (Transactions & Row-level locking)
- **Async**: Celery + Redis (Background tasks & scheduling)
- **Payments**: Stripe API (Webhooks & Idempotency)
- **Infrastructure**: Docker & Docker Compose

##  Key Features

- **Concurrency Control**: Uses PostgreSQL `select_for_update` within atomic transactions to prevent Race Conditions.
- **Background Cleanup**: "Zombie" reservations (unpaid bookings) are automatically released after 15 minutes using Celery delayed tasks.
- **Reliable Payments**: Booking confirmation happens strictly via Stripe Webhooks (signature verification included), not frontend signals.
- **Dynamic Hall Layouts**: Stores cinema configuration as JSON to support complex seat maps (gaps, VIP zones).

##  Architecture Decisions

### Why `select_for_update`?
In a high-load environment, checking if `seat.is_available` in Python code is not enough. Between the check and the save, another request could modify the data.
I implemented **Pessimistic Locking** at the database level. This forces the DB to lock the specific seat row during a transaction, making other concurrent requests wait until the first transaction commits or rolls back.

### Why Celery for cleanup?
Using a cron job (Celery Beat) every minute to clean expired bookings is inefficient and creates DB spikes. Instead, I use **Per-Task Delays**. When a booking is created, a specific cleanup task is scheduled to run exactly 15 minutes later. If the order is paid, the task simply exits.

##  How to Run

### Clone the repo
```bash
git clone https://github.com/yourusername/seatlock-api.git
cd seatlock-api
```

### Environment Setup
Create a `.env` file in the root directory (see `.env.example`).

### Launch with Docker
```bash
docker-compose up --build
```
The API will be available at http://localhost:8000/.

### Create Superuser
```bash
docker-compose exec backend python manage.py createsuperuser
```
