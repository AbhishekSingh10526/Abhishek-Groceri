# Groceri - Online Grocery Store

## Overview

Groceri is a web-based grocery store application built with Flask. It allows customers to browse products organized by categories, add items to a shopping cart, and place orders. Admin users can manage categories and products (CRUD operations). The app features user authentication, role-based access control (admin vs regular user), and order/transaction tracking.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Framework
- **Flask** (Python) serves as the web framework
- Server-side rendered templates using **Jinja2**
- Session-based authentication stored in Flask's `session` object
- Custom decorators (`@auth_required`, `@admin_required`) handle route protection

### Database & ORM
- **Flask-SQLAlchemy** as the ORM layer
- Default database is **SQLite** (`sqlite:///site.db`) for local development
- Supports **PostgreSQL** via the `DATABASE_URL` environment variable (with automatic `postgres://` to `postgresql://` URL fix for Heroku/Render compatibility)
- `psycopg2-binary` is included for PostgreSQL connectivity
- Database tables are auto-created on startup via `db.create_all()`
- A default admin user (`admin`/`admin`) is seeded on first run

### Data Models
- **User** — username, password hash (via Werkzeug), name, is_admin flag
- **Category** — name; has many Products
- **Product** — name, category_id (FK), quantity, price, manufacture date; has many Cart items and Orders
- **Cart** — user_id (FK), product_id (FK) — links users to products in their cart
- **Order** and **Transaction** — referenced in routes/templates but not fully defined in the provided `models.py` (these models need to be completed; Order likely has quantity, price, product_id, transaction_id; Transaction likely has datetime, total, user_id)

### Missing/Incomplete Code
- The `models.py` file is missing the `Order` and `Transaction` model definitions, but `routes.py` imports them. These need to be added.
- The `routes.py` file is truncated — many route handlers are incomplete or missing (profile update, login, register, logout, cart operations, order placement, category/product CRUD endpoints)
- The `Cart` model appears to be missing a `quantity` field (referenced in `cart.html` template as `item.quantity`)
- Some HTML templates have unclosed tags or are truncated

### Frontend
- **Bootstrap 5.3** for CSS framework (loaded via CDN)
- **Font Awesome 6.4** for icons (loaded via CDN)
- Server-side rendered Jinja2 templates with a base layout (`layout.html`) and template inheritance
- Flash messages displayed with Bootstrap alert styling (success/danger based on message content)
- Navigation dynamically shows links based on authentication state and admin role

### Project Structure
```
app.py          — App factory, DB init, admin seeding
config.py       — Environment-based config (uses dotenv)
models.py       — SQLAlchemy models
routes.py       — All route handlers and decorators
templates/
  layout.html   — Base template with nav, flash messages
  nav.html      — Navigation bar partial
  searchbar.html — Search/filter partial
  index.html    — Home page with product listings
  login.html    — Login form
  register.html — Registration form
  profile.html  — User profile editing
  cart.html     — Shopping cart view
  orders.html   — Order history view
  admin.html    — Admin dashboard
  category/     — Category CRUD templates (add, edit, delete, show)
  product/      — Product CRUD templates (add, edit, delete)
```

### Authentication
- Password hashing via Werkzeug's `generate_password_hash` / `check_password_hash`
- Session-based auth using Flask's built-in session (`session['user_id']`)
- Two decorator functions for access control: `auth_required` and `admin_required`

### Key Design Decisions
- **Monolithic Flask app**: All routes in a single file, all models in a single file. Simple but may need refactoring for scale.
- **No migration tool**: Uses `db.create_all()` instead of Flask-Migrate/Alembic. Schema changes require manual handling.
- **SQLite as default with PostgreSQL support**: Enables easy local development while supporting production PostgreSQL deployments.

## External Dependencies

### Python Packages (from requirements.txt)
- **Flask 2.3.2** — Web framework
- **Flask-SQLAlchemy 3.0.5** — ORM integration
- **Flask-RESTful 0.3.10** — REST API support (included but not actively used in visible code)
- **SQLAlchemy 2.0.19** — Database ORM
- **Werkzeug 2.3.8** — Password hashing, HTTP utilities
- **python-dotenv 1.0.0** — Environment variable loading
- **gunicorn 21.2.0** — Production WSGI server
- **psycopg2-binary 2.9.9** — PostgreSQL adapter
- **Jinja2 3.1.2** — Template engine

### CDN Resources
- Bootstrap 5.3.1 (CSS and JS)
- Font Awesome 6.4.2

### Environment Variables
- `DATABASE_URL` — Database connection string (defaults to SQLite)
- `SECRET_KEY` — Flask session secret key
- `SQLALCHEMY_DATABASE_URI` — Alternative DB URI (via dotenv/config.py)
- `SQLALCHEMY_TRACK_MODIFICATIONS` — SQLAlchemy config flag