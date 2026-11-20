# 🎂 Sweet Delights Artisan Bakery Management System (BMS)

A modern, responsive, production-style, role-based Bakery ERP and Point of Sale (POS) web application built with **Python Flask**, **SQLAlchemy ORM**, **MySQL**, **Bootstrap 5**, and **Chart.js**.

Designed and engineered for a **Software Engineering college project demonstration** and real-world bakery operations.

---

## 🌟 1. Project Overview & Business Flow

Sweet Delights replaces manual paper order pads, carbon-copy bill receipts, and fragmented inventory notebooks with a unified, automated digital management system.

### Core Business Flow:
$$\text{Customer/Walk-in} \longrightarrow \text{Browse/POS} \longrightarrow \text{Cart \& Checkout} \longrightarrow \text{Payment Recorded} \longrightarrow \text{Kitchen Display (KDS)} \longrightarrow \text{Preparation \& Oven} \longrightarrow \text{Ready \& Boxed} \longrightarrow \text{Delivered} \longrightarrow \text{Bill/Invoice} \longrightarrow \text{Sales Analytics Updated}$$

---

## 🚀 2. Technology Stack

- **Backend Framework**: Python 3.10+ / 3.14 (Flask 3.x)
- **Database & ORM**: MySQL (with PyMySQL) & SQLAlchemy ORM
- **Session & Auth**: Flask-Login, Werkzeug password hashing (PBKDF2/SHA256)
- **Frontend Architecture**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3.3, Bootstrap Icons
- **Data Visualization**: Chart.js 4.4.x (7 interactive dynamic dashboards)
- **Invoice & PDF Engine**: ReportLab 5.x & Browser Print Engine with `@media print`
- **Testing Framework**: Pytest 8.x/9.x

---

## 🛡️ 3. Role-Based Access Control (RBAC) & Demo Accounts

The system enforces strict multi-role authorization. Each role sees only the views and actions permitted for their domain. Unauthorized attempts are blocked with a customized **403 Forbidden** page.

| Role | Username | Password | Dedicated Access & Dashboard |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `admin123` | Full ERP Control: User Accounts, Staff, Products, Categories, Orders, Global Settings |
| **Manager** | `manager` | `manager123` | Analytics Command Center, 7 Interactive Charts, Financial Reports, CSV Export |
| **Cashier** | `cashier` | `cashier123` | POS Terminal, Quick Product Grid, Customer Billing, Invoices, Print/PDF/Share |
| **Baker / Kitchen** | `baker` | `baker123` | Kitchen Display System (KDS): Live Queue, Oven Prep, Status Flow, Custom Cake Studio |
| **Store Keeper** | `store` | `store123` | Raw Materials Inventory, Stock In/Out, Stock Audits, Suppliers, Low Stock Alerts |
| **Customer** | `customer` | `customer123` | Artisan Storefront, Menu, Custom Cake Studio, Cart, Checkout, Order Tracking, Invoices |

*Note: All passwords are securely stored as cryptographic hashes using Werkzeug; plaintext credentials are never saved or exposed.*

---

## 📦 4. System Architecture & Project Structure

```text
SE Project/
│
├── app.py                      # Application factory, blueprints, context processors, CLI
├── config.py                   # Environment-driven configuration (MySQL / SQLite fallback)
├── extensions.py               # Shared extensions (SQLAlchemy, LoginManager)
├── requirements.txt            # Python dependencies
├── .env.example                # Example environment configuration
├── .env                        # Local environment variables
├── README.md                   # Complete documentation and setup manual
│
├── models/                     # SQLAlchemy Models (MVC Pattern)
│   ├── __init__.py             # Exports all models
│   ├── user.py                 # User, Customer, Staff models
│   ├── product.py              # Category, Product models
│   ├── order.py                # Order, OrderItem, Bill models
│   ├── custom_cake.py          # CustomCakeOrder model
│   ├── inventory.py            # Ingredient, InventoryTransaction models
│   ├── supplier.py             # Supplier model
│   └── settings.py             # SystemSetting model
│
├── routes/                     # Blueprint Controllers
│   ├── __init__.py             # Exports all blueprints
│   ├── auth.py                 # Login, Register, Profile, Logout
│   ├── customer.py             # Storefront, Menu, Cart, Checkout, Custom Cake, Tracking
│   ├── cashier.py              # POS Terminal, Billing, Receipts, Transactions
│   ├── baker.py                # Kitchen Display System (KDS), Status transitions
│   ├── inventory.py            # Raw materials, Stock In/Out, Adjustments, Suppliers
│   ├── admin.py                # User CRUD, Product CRUD, Categories, Global Settings
│   ├── manager.py              # KPIs, 7 Chart.js Visualizations, CSV Exports
│   └── api.py                  # Dynamic search and JSON calculations
│
├── services/                   # Business Logic & Computational Layer
│   ├── __init__.py
│   ├── billing_service.py      # Decimal-safe subtotal, tax, discount calculations
│   ├── inventory_service.py    # Stock movement with negative stock protection
│   ├── order_service.py        # Order creation, unique numbering, status machine
│   └── report_service.py       # KPI analytics, charts data, CSV streaming
│
├── utils/                      # Helper Utilities & Decorators
│   ├── __init__.py
│   ├── decorators.py           # Strict @role_required, @anonymous_only
│   ├── pdf_generator.py        # ReportLab PDF invoice builder
│   └── helpers.py              # Currency formatter, file upload security
│
├── database/                   # Database Assets
│   ├── schema.sql              # MySQL DDL Schema (InnoDB, utf8mb4, foreign keys)
│   └── seed.py                 # Realistic sample data seeder
│
├── templates/                  # Jinja2 HTML5 Templates
│   ├── base.html               # Master layout, navigation, flash messages, footer
│   ├── auth/                   # login.html (1-click demo filler), register.html
│   ├── customer/               # home.html, menu.html, cart.html, checkout.html, etc.
│   ├── cashier/                # pos.html, invoice_view.html, orders.html, transactions.html
│   ├── baker/                  # dashboard.html (KDS Kanban), custom_cakes.html
│   ├── inventory/              # dashboard.html, stock_movement.html, suppliers.html, alerts.html
│   ├── admin/                  # dashboard.html, users.html, products.html, categories.html, settings.html
│   ├── manager/                # dashboard.html (Charts), reports.html
│   └── errors/                 # 400.html, 401.html, 403.html, 404.html, 500.html
│
├── static/                     # Static Assets
│   ├── css/                    # custom.css, pos.css
│   ├── js/                     # main.js, pos.js, charts.js
│   └── uploads/                # Product photos, custom cake reference uploads
│
└── tests/                      # Automated Test Suite (Pytest)
    ├── conftest.py             # Fixtures and test client setup
    ├── test_auth.py            # Authentication & role authorization tests
    ├── test_products.py        # Product catalog & CRUD tests
    ├── test_cart_order.py      # Cart, checkout, tracking tests
    ├── test_inventory.py       # Stock In/Out, negative stock protection tests
    └── test_billing_reports.py # Billing calculations & CSV export tests
```

---

## 💡 5. Module Highlights & Features

### 🍰 Customer Storefront
- **Artisan Showcase**: Warm cream, chocolate brown, and caramel gold aesthetic.
- **Menu Catalog**: Instant live search, category filtering (Cakes, Breads, Pastries, Cookies), price range filters, availability filter, and sorting.
- **Product Details**: High-resolution image showcase, ingredient breakdown, and quantity selector.
- **Cart Management**: Real-time quantity steppers (+/-), item removal, subtotal, tax calculation, and instant grand total.
- **Order Tracking**: Visual 5-step progress stepper (`Pending` $\rightarrow$ `Confirmed` $\rightarrow$ `Preparing` $\rightarrow$ `Ready` $\rightarrow$ `Delivered`).
- **Invoice Center**: View, print, and download PDF receipts for past purchases.

### 🎨 Custom Cake Studio
- Dedicated ordering interface for celebration tiers, wedding fondants, and birthday novelty cakes.
- Custom options: Cake Type, Flavour, Size (0.5 kg to 5.0 kg), Quantity, Delivery Date & Time, Inscription Messages, Dietary instructions (Eggless/Nut-free), and Reference Photo Upload.
- Separate view on the Kitchen Display System for cake decorators.

### 💳 Cashier / POS (Point of Sale)
- **Fast Billing Grid**: Touch-friendly product tiles with quick category filter pills.
- **Flexible Customer Modes**: 1-click Walk-in mode, Registered Customer search, or on-the-fly New Customer registration.
- **Discount & Tax Calculator**: Supports flat dollar discounts or percentage discounts with automatic tax computation.
- **Multi-Payment Modes**: Cash, Card, and instant UPI.
- **Instant Receipts**: Print thermal/standard invoice, download PDF invoice, or share via browser Web Share API.

### 👨‍🍳 Baker / Kitchen Display System (KDS)
- Kanban queue columns: **New Orders (Pending)**, **In Preparation (Ovens)**, **Ready for Pickup/Delivery**, and **Custom Cake Tasks**.
- Order cards show customer, items, quantities, special instructions, and timers.
- One-click workflow transition buttons: *Accept Order*, *Start Prep*, *Mark Ready*, *Mark Delivered*.

### 📦 Raw Material Inventory & Store Keeper
- Real-time tracking of ingredients: Flour, Sugar, European Butter, Eggs, Milk, Chocolate, Cream, Yeast, Cocoa, Vanilla, and Packaging Boxes.
- Stock operations: **Stock In** (restock receipts), **Stock Out** (kitchen consumption), and **Stock Audits** (physical count adjustments).
- **Negative Stock Prevention**: Built-in validation prevents warehouse stock from dropping below zero.
- **Prominent Low Stock Warning**: Prominent danger alert triggers automatically whenever `quantity_available <= reorder_level`.
- **Supplier Directory**: Manage vendor contacts, supplied materials, and order histories.

### 📊 Manager Dashboard & Chart.js Analytics
- High-level KPIs: Today's Sales, Weekly Sales, Monthly Sales, Pending Orders, Completed Orders, Low Stock Alerts.
- **7 Dynamic Chart.js Visualizations**:
  1. *Daily Sales Trend* (7-day line chart with gradient fill)
  2. *Weekly Sales Performance* (4-week comparative bar chart)
  3. *Monthly Sales Volume* (6-month bar chart)
  4. *Orders by Status* (Doughnut distribution)
  5. *Top-Selling Products* (Horizontal bar ranking)
  6. *Sales by Category* (Pie chart breakdown)
  7. *Inventory Stock vs Safety Reorder Level* (Comparative bar chart)
- **Comprehensive Reports Engine**: Filter by date range (Today, Yesterday, This Week, This Month, Custom Date Range) and export to CSV.

### ⚙️ Administrator Command Center
- Complete User Management: Add user, edit profiles, toggle active status (disable/enable), change roles, reset passwords.
- Product Catalog CRUD: Add new items with image upload, edit details, toggle availability, delete items.
- Category Management: Create, edit, and organize bakery categories.
- Global System Settings: Bakery Name, Tagline, Phone, Email, Address, Sales Tax %, and Default Discounts.

---

## 🧮 6. Billing & Mathematical Precision

All monetary computations use decimal-safe calculations:

$$\text{Subtotal} = \sum (\text{Quantity}_i \times \text{Unit Price}_i)$$

$$\text{Discount} = \min(\text{Discount Input}, \text{Subtotal})$$

$$\text{Taxable Amount} = \max(0, \text{Subtotal} - \text{Discount})$$

$$\text{Tax} = \text{Taxable Amount} \times \left(\frac{\text{Tax Rate}}{100}\right)$$

$$\text{Grand Total} = \max(0, \text{Subtotal} - \text{Discount} + \text{Tax})$$

- Values are rounded using `ROUND_HALF_UP` to two decimal places.
- Discounts are capped to prevent negative bills.

---

## 🛠️ 7. Installation & Setup Instructions

### Prerequisites
- Python 3.10, 3.11, 3.12, 3.13, or 3.14
- (Optional) MySQL Server 8.0+ or MariaDB (or use the built-in SQLite database engine for zero-configuration setup)

### Step 1: Clone or Navigate to the Workspace
```powershell
cd "c:\Users\nallu\OneDrive\Desktop\SE Project"
```

### Step 2: Create and Activate a Virtual Environment (Optional but Recommended)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```

#### Database Engine Choice:
- **Default (Zero-Config SQLite)**: Leave `DATABASE_URL` blank in `.env`. The system automatically creates and manages `bakery.db`.
- **MySQL Mode**: In `.env`, set:
  ```env
  DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/bakery_db
  # Or:
  USE_MYSQL=true
  MYSQL_HOST=localhost
  MYSQL_PORT=3306
  MYSQL_USER=root
  MYSQL_PASSWORD=your_password
  MYSQL_DATABASE=bakery_db
  ```
  And import `database/schema.sql` into MySQL if desired:
  ```bash
  mysql -u root -p < database/schema.sql
  ```

### Step 5: Seed the Database with Realistic Demo Data
Run the database seeder to populate all roles, products, categories, ingredients, suppliers, and sample orders:
```powershell
python database/seed.py
```
*(Or run `flask seed-db`)*

### Step 6: Launch the Bakery Management Application
```powershell
python app.py
```
Open your web browser and navigate to:
```text
http://127.0.0.1:5000
```

---

## 🧪 8. Testing Guide

### Automated Pytest Suite
The application includes 24 automated tests covering authentication, RBAC authorization, product CRUD, cart workflows, order lifecycle, negative stock prevention, low-stock detection, billing precision, and CSV reports:

```powershell
python -m pytest tests/ -v
```

**Expected Result:**
```text
tests/test_auth.py::test_registration PASSED
tests/test_auth.py::test_login_success PASSED
tests/test_auth.py::test_login_invalid_credentials PASSED
tests/test_auth.py::test_customer_unauthorized_from_admin PASSED
tests/test_auth.py::test_customer_unauthorized_from_pos PASSED
tests/test_auth.py::test_admin_authorized PASSED
tests/test_auth.py::test_cashier_authorized PASSED
tests/test_auth.py::test_baker_authorized PASSED
tests/test_auth.py::test_store_keeper_authorized PASSED
tests/test_billing_reports.py::test_billing_calculation_exactness PASSED
tests/test_billing_reports.py::test_billing_negative_discount_capping PASSED
tests/test_billing_reports.py::test_dashboard_summary_and_csv_generation PASSED
tests/test_cart_order.py::test_cart_workflow PASSED
tests/test_cart_order.py::test_checkout_and_order_creation PASSED
tests/test_cart_order.py::test_custom_cake_order_creation PASSED
tests/test_inventory.py::test_stock_in PASSED
tests/test_inventory.py::test_stock_out PASSED
tests/test_inventory.py::test_negative_stock_prevention PASSED
tests/test_inventory.py::test_low_stock_detection PASSED
tests/test_products.py::test_menu_page PASSED
tests/test_products.py::test_product_search PASSED
tests/test_products.py::test_product_details_page PASSED
tests/test_admin_create_product PASSED
tests/test_admin_edit_product PASSED
======================== 24 passed in tests ========================
```

---

## 📋 9. Manual Demonstration Walkthrough

For college project presentation and review, follow these scenarios:

### Scenario 1: Customer Online Order & Live Tracking
1. Open `http://127.0.0.1:5000` and click **Sign In**.
2. Click the **Customer** 1-click button (`customer` / `customer123`).
3. Click **Menu & Products**, search for *"Chocolate Truffle"*, and click **Add to Cart**.
4. Click **Cart**, verify subtotal, tax, and total. Click **Proceed to Checkout**.
5. Select payment mode (Cash/Card/UPI) and click **Confirm & Place Order**.
6. View the real-time **Order Tracking** screen with the 5-step progress bar.

### Scenario 2: Kitchen Display System (Baker)
1. Sign out and sign in as **Baker** (`baker` / `baker123`).
2. Notice the order placed in Scenario 1 appears under **New Orders**.
3. Click **Accept Order** $\rightarrow$ moves to **In Preparation**.
4. Click **Start Baking / Prep** $\rightarrow$ status updates to **Preparing**.
5. Click **Mark As Ready!** $\rightarrow$ status updates to **Ready**.
6. Switch back to the customer tab or tracking link: status changes to *Packed & Ready*!

### Scenario 3: Cashier Point of Sale (POS)
1. Sign in as **Cashier** (`cashier` / `cashier123`) $\rightarrow$ automatically loads `/cashier/pos`.
2. Select product tiles from the menu.
3. Test quantity controls (+/-) and apply a \$2.00 discount.
4. Select payment mode (UPI/Card/Cash) and click **Charge & Generate Invoice**.
5. The professional invoice preview appears. Test **Print Receipt** and **Download PDF**.

### Scenario 4: Store Keeper Inventory & Negative Stock Prevention
1. Sign in as **Store Keeper** (`store` / `store123`).
2. Observe the prominent red banner for **Low Stock Warnings** (e.g. Butter, Chocolate).
3. Click **In** on Flour, add 20 kg $\rightarrow$ stock updates and audit log records the transaction.
4. Click **Out** on Butter (5 kg available) and enter 25 kg $\rightarrow$ system blocks the transaction with an *Insufficient Stock* alert!

### Scenario 5: Manager Analytics & Financial Reports
1. Sign in as **Manager** (`manager` / `manager123`).
2. Review the 7 Chart.js charts: Daily sales, weekly sales, monthly volume, top-selling products, and stock health.
3. Go to **Financial Reports & Export**, choose a date filter, and click **Export to CSV**.

### Scenario 6: Administrator Control
1. Sign in as **Administrator** (`admin` / `admin123`).
2. Go to **User Accounts** $\rightarrow$ create staff or toggle account status.
3. Go to **Product Catalog** $\rightarrow$ add/edit items or change retail prices.
4. Go to **System Settings** $\rightarrow$ update bakery name, tax rate, or currency.

---

## 🔒 10. Security Implementation

- **Password Encryption**: Werkzeug PBKDF2 with SHA-256 password hashing. Passwords are never stored or logged in plaintext.
- **SQL Injection Defense**: SQLAlchemy ORM parametrized queries throughout all models and services.
- **Role-Based Authorization**: Custom `@role_required` decorators protect administrative and financial routes. Unauthorized attempts trigger HTTP 403 Forbidden.
- **Session Protection**: HttpOnly cookie configuration, SameSite Lax policy, and automated session expiry.
- **File Upload Safeguards**: Secure file naming (`secure_filename`), UUID prefixing, and strict extension whitelisting (`png`, `jpg`, `jpeg`, `webp`).
- **Data Integrity**: Safe decimal rounding, negative stock prevention, and minimum order quantity enforcement.

---

## 📄 License & Academic Attribution
Developed for the **Software Engineering Project Evaluation**. Demonstrates full-stack modular architecture, relational database modeling, role-based authorization, Point of Sale hardware integration readiness, and modern responsive design.
#   - s w e e t - d e l i g h t s - b m s  
 