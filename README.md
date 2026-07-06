# AuraMarket - Django Production E-Commerce Setup Guide (cPanel & Local Ready)

This directory contains the full, standalone Django implementation of **AuraMarket**, featuring a **Sleek Slate & Minimal Gold** design, Bengali/English support, session-based guest checkout, and hidden management controls.

---

## 🚀 Local Development & Testing Instructions

Follow these steps to run AuraMarket locally on your machine with Python & Django:

### 1. Install Dependencies
Make sure Python 3.9+ is installed on your system.
```bash
pip install -r requirements.txt
```

### 2. Apply Database Migrations
Create SQLite database tables for Products, Orders, Order Items, and Price Alerts:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Superuser / Staff Account
Create an administrative staff account to test the Django Admin Panel (`/admin/`) and Management Hub (`/management-hub/`):
```bash
python manage.py createsuperuser
```
*(Enter your desired username, email, and password)*

### 4. Seed Initial Products (Optional)
Start the server and visit `/management-hub/` or use Django admin at `/admin/` to add products, set discount prices, and manage stock levels.

### 5. Start Local Development Server
Launch the Django server:
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## 📁 Django Project Directory Structure

```
├── manage.py                   # Django CLI entry point
├── passenger_wsgi.py           # cPanel WSGI launcher script
├── requirements.txt            # Python dependencies (Django, Pillow, etc.)
├── README.md                   # Setup guide
├── auramarket/                 # Core Django configuration package
│   ├── settings.py             # Database, CSRF, and static file settings
│   ├── urls.py                 # Core URL router
│   └── wsgi.py
└── shop/                       # E-Commerce Application Package
    ├── admin.py                # Django Admin interface for Products & Orders
    ├── models.py               # Product, Order (with tracking number), OrderItem, PriceAlert
    ├── urls.py                 # Application URLs & JSON API routes
    ├── views.py                # Shop, Tracking, Seller Console & AJAX checkout views
    ├── static/                 # Static CSS, JS & Assets
    │   ├── css/custom.css      # 3D Card tilt, glassmorphism & typography CSS
    │   └── js/main.js          # Cart, Toast Notifications, bKash/Nagad/CoD checkout
    └── templates/              # Django HTML Templates
        └── shop/
            ├── base.html       # Base layout with Tailwind CDN & Toast container
            ├── catalog.html    # Product grid with 3D card tilt, search bar & sort dropdown
            ├── track.html      # Real-time order tracking timeline
            ├── management_hub.html # Owner Management Hub & Order Fulfillment
            └── components/
                ├── header.html
                ├── cart_drawer.html
                └── wishlist_drawer.html
```
## 🌐 cPanel Deployment Steps

1. Upload files to cPanel File Manager.
2. Create Python App in cPanel (**Setup Python App**).
3. Activate virtualenv and run `pip install -r requirements.txt`.
4. Run `python manage.py migrate` and `python manage.py collectstatic`.
5. Restart Python App in cPanel.
