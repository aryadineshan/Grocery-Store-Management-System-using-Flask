# Grocery-Store-Management-System-Flask-Framework-
A web application for managing grocery store operations, including inventory, billing, and sales analytics, built using Python (Flask), HTML/CSS, JavaScript, and Matplotlib for data visualization.


## Tech Stack

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript
- **Database**: MySQL (configured via XAMPP)
- **Data Visualization**: Matplotlib
- **Database Integration**: `mysql.connector` using raw SQL queries



## Key Features

- Admin and Employee login/registration system
- Product CRUD operations (add, update, delete, view)
- Real-time stock and inventory management
- Billing system with total cost calculation
- Sales data tracking and visualization using Matplotlib
- Admin and Employee access roles



## Database Setup (MySQL using XAMPP)

1. Open **XAMPP** and start **Apache** and **MySQL**.
2. Open **phpMyAdmin** at `http://localhost/phpmyadmin`.
3. You **do not need to create the database manually**. The Flask app auto-creates it as `testgrocerystore` on first run via this code:

```python
query = "CREATE DATABASE IF NOT EXISTS testgrocerystore"

### Note:
Replace `your_host`, `your_user`, `your_password`, and `your_database` in `main.py` with your actual MySQL credentials before running.

