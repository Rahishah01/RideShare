<p align="center">
  <img src="static/images/logo.png" width="140" alt="RideShare Logo">
</p>

<h1 align="center">RideShare</h1>

<p align="center">
A modern full-stack ride-sharing platform built with Django that connects drivers and passengers through a clean, production-ready web application.
</p>

> A production-ready ride-sharing platform featuring passenger booking, driver management, and a custom administrative Command Center.

<p align="center">

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.2-092E20?style=for-the-badge&logo=django)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Render](https://img.shields.io/badge/Render-Deployed-5C4EE5?style=for-the-badge&logo=render)
[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Visit_Website-7AC943?style=for-the-badge)](https://rideshare-9p5s.onrender.com)

</p>

---

# 🌐 Live Demo

### https://rideshare-9p5s.onrender.com

> **Note:** This project is hosted on Render's free tier. The website may take 30–60 seconds to wake up if it has been inactive.

---

# 📖 Overview

RideShare is a full-stack web application that allows drivers to publish available rides while passengers can search, reserve seats, and manage their bookings through a modern and intuitive interface.

Unlike a basic CRUD project, RideShare includes a **custom-built administrative Command Center** that provides platform analytics, user management, trip management, booking administration, and review management.

The application was designed with scalability, usability, and clean UI/UX in mind.

---

# ✨ Features

## 👤 Passenger

- Create an account
- Secure authentication
- Search available rides
- Reserve seats
- Cancel reservations
- View booking history
- Manage personal profile

---

## 🚗 Driver

- Publish new rides
- Manage offered rides
- Edit ride information
- Cancel trips
- View passengers
- Driver dashboard
- Earnings estimation

---

## 🛡️ Administrator

- Custom Command Center
- Platform analytics
- User management
- Trip management
- Booking management
- Review management
- Financial overview
- Popular routes
- Top drivers

---

# 📸 Screenshots

## 🏠 Homepage

<img width="1917" height="866" alt="Screenshot 2026-07-22 223957" src="https://github.com/user-attachments/assets/f813f9a2-441a-496d-99d3-d13cdec4bbe4" />


---

## 🔍 Find a Ride

<img width="1917" height="866" alt="Screenshot 2026-07-22 224015" src="https://github.com/user-attachments/assets/ca267fd7-5b5b-4965-9f14-248d7fa8159e" />


---

## 🚘 Ride Details

<img width="1917" height="868" alt="Screenshot 2026-07-22 224336" src="https://github.com/user-attachments/assets/f13e50a0-3377-4503-bb9c-3cbe2202cdce" />


---

## ➕ Offer a Ride

<img width="774" height="83" alt="Screenshot 2026-05-06 052200" src="https://github.com/user-attachments/assets/2a3d1633-f0a9-4f0a-8bc1-42763329bc51" />


---

## 📊 Driver Dashboard

<img width="1917" height="862" alt="Screenshot 2026-07-22 224353" src="https://github.com/user-attachments/assets/22c2cc96-fde9-42c5-a8b1-511c424d3b7a" />


---

## 👤 User Profile

<img width="1917" height="866" alt="Screenshot 2026-07-22 224529" src="https://github.com/user-attachments/assets/4aa8f404-99ef-4c1c-8a4c-81ef8ccd748e" />


---

## 🛡️ Command Center

<img width="1917" height="862" alt="Screenshot 2026-07-22 225116" src="https://github.com/user-attachments/assets/5eb69feb-3fbe-4c4f-b985-8b1d08a29e9c" />


---

# 🛠️ Technology Stack

| Category | Technologies |
|------------|----------------|
| Backend | Python, Django |
| Frontend | HTML5, CSS3, JavaScript |
| Database | SQLite (Development), PostgreSQL (Production) |
| Deployment | Render |
| Version Control | Git & GitHub |
| Static Files | WhiteNoise |
| WSGI Server | Gunicorn |

---

# 🏗️ Project Structure

```
RideShare
│
├── core/
├── rideshare/
├── static/
├── templates/
├── screenshots/
├── manage.py
├── requirements.txt
└── README.md
```

---

# 🚀 Installation

### Clone the repository

```bash
git clone https://github.com/Rahishah01/RideShare.git
```

Move into the project

```bash
cd RideShare
```

Create virtual environment

Windows

```bash
python -m venv venv
venv\Scripts\activate
```

Mac / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run migrations

```bash
python manage.py migrate
```

Create an administrator

```bash
python manage.py createsuperuser
```

Start the development server

```bash
python manage.py runserver
```

Visit

```
http://127.0.0.1:8000/
```

---

# 📂 Environment Variables

The project uses environment variables for production deployment.

```
SECRET_KEY
DEBUG
DATABASE_URL
ALLOWED_HOSTS
CSRF_TRUSTED_ORIGINS
```

Sensitive credentials are **never stored** inside the repository.

---

# ⭐ Highlights

- Responsive modern UI
- Production deployment on Render
- PostgreSQL database
- Secure authentication
- Custom Command Center
- Driver & Passenger workflows
- Booking management
- Seat availability validation
- Duplicate booking prevention
- Automatic seat restoration after cancellation
- GitHub integrated deployment

---

# 🔮 Future Improvements

- Google Maps integration
- Dynamic pricing
- AI ride recommendations
- Email verification
- Password reset emails
- Ride notifications
- Ratings & Reviews improvements
- Mobile application
- Payment integration

---

## 👨‍💻 Author

**Rahi Shah**

Computer Science student passionate about Full-Stack Development and Backend Engineering.

- GitHub: https://github.com/Rahishah01
- LinkedIn: https://www.linkedin.com/in/rahi-shah-/

---

# 📄 License

This repository is shared publicly for **portfolio and educational purposes**.

Please do not copy, redistribute, or commercially deploy this project without permission.
