# Zeniti Portfolio 🚀

**Zeniti** is a high-end, dynamic full-stack developer portfolio and service booking platform built with Django. It features a hyper-precision hacking aesthetic, real-time Telegram integration, a native appointment calendar, anti-spam protections, and robust content management capabilities.

## 🌟 Key Features

- **Hacker/Minimal Aesthetics:** Striking dark mode themes (Default & Hacker) with responsive design and subtle glow effects.
- **Dynamic Content Management:** Easily manage FAQs, Projects, Services, and incoming Bookings directly from the Django Admin Panel.
- **Native Appointment Booking:** Interactive calendar for clients to book available time slots directly.
- **Telegram Bot Integration:** Get instant notifications on your phone whenever a client messages or books an appointment.
- **Anti-Spam Security:** Invisible Honeypot fields implemented to block bots without hurting User Experience.
- **Production Ready:** Pre-configured for deployment (Whitenoise for static files, Secure Environment Variables, custom 404/500 pages).

---

## 🛠 Tech Stack

- **Backend:** Python + Django
- **Frontend:** Vanilla JavaScript, HTMX (for dynamic forms), HTML5, CSS3 (Glassmorphism & Custom Themes)
- **Database:** SQLite (default) / Configurable for PostgreSQL
- **Integrations:** Telegram Bot API
- **Deployment Utilities:** Whitenoise

---

## 🚀 Local Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/achiko10/achiko7.git
   cd achiko7
   ```

2. **Create a Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Environment Variables:**
   Create a `.env` file (or export in your terminal) with your secrets:
   ```env
   DJANGO_SECRET_KEY=your_secret_key_here
   DJANGO_DEBUG=True
   TELEGRAM_BOT_TOKEN=your_bot_token
   TELEGRAM_CHAT_ID=your_chat_id
   ```

5. **Run Migrations & Start Server:**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

---

## ☁️ Deployment Instructions (PythonAnywhere / VPS)

1. Upload your code to the server using `git clone`.
2. Configure **Environment Variables** securely on your host (ensure `DJANGO_DEBUG=False`).
3. Set `DJANGO_ALLOWED_HOSTS` to your assigned domain (e.g., `yourdomain.com`).
4. Run `python manage.py collectstatic` to gather static files using Whitenoise.
5. Apply migrations: `python manage.py migrate`.
6. Restart your WSGI server to reflect the changes.

---

*Designed and Developed by [achiko10]*
