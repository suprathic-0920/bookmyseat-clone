# 🎬 BookMySeat - Movie Booking Platform (Django)

A full-stack movie and event booking web application built using **Django**. This project is a clone of popular movie ticketing platforms like BookMyShow, designed with modern UI/UX and a robust backend.

## 🚀 Features

- **User Authentication:** Sign up, Login, Password Reset.
- **Dynamic City Selection:** Browse movies playing in your selected city.
- **Movie & Theater Listings:** View now showing movies, theater details, and upcoming events.
- **Interactive Seat Booking:** 
  - Visual seat map with available, locked, and booked status.
  - Concurrency-safe seat locking (so two users can't book the same seat simultaneously).
- **Payment Integration:** Secure checkout using **Stripe**.
- **Automated Email Notifications:** E-tickets sent directly to the user's email upon successful payment.
- **Admin Dashboard:** Manage movies, theaters, showtimes, users, and bookings (via Django Admin).
- **Responsive Design:** Optimized for desktop and mobile viewing with smooth animations.

## 🛠️ Tech Stack

- **Backend:** Python, Django
- **Frontend:** HTML5, CSS3, Bootstrap 5, Vanilla JS, GSAP (for animations)
- **Database:** PostgreSQL (Production via Neon) / SQLite (Local)
- **Payments:** Stripe API
- **Task Queue & Cache:** Celery, Redis (for local async tasks and caching)
- **Deployment:** Vercel

## 💻 Local Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/suprathic-0920/bookmyseat-clone.git
   cd bookmyseat-clone
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Create a `.env` file in the root directory and add:
   ```env
   STRIPE_PUBLIC_KEY=your_stripe_public_key
   STRIPE_SECRET_KEY=your_stripe_secret_key
   STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
   EMAIL_HOST_USER=your_email@gmail.com
   EMAIL_HOST_PASSWORD=your_app_password
   ```

5. **Run Migrations & Seed Data:**
   ```bash
   python manage.py migrate
   python seed_movies.py
   python refresh_showtimes.py
   ```

6. **Start the Development Server:**
   ```bash
   python manage.py runserver
   ```
   Visit `http://127.0.0.1:8000` in your browser.

## 🌍 Production Deployment (Vercel)

This app is configured to be deployed on **Vercel** with a Serverless architecture.

- **Vercel Settings:** Set `VERCEL=1` in the Vercel Environment Variables to disable long-running workers (Celery/Channels) and switch to in-memory caching.
- **Database:** Uses a cloud **PostgreSQL** database (via Neon). Set the `DATABASE_URL` in Vercel.

---
*Developed as an internship project.*
