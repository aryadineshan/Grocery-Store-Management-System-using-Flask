
from flask import Flask, render_template, request, redirect, url_for, flash, session #importing modules from flask
import matplotlib #for data visualisation
matplotlib.use('Agg') #agg is the default backend which generates and display graphs as PNGs. 
import matplotlib.pyplot as plt
import mysql.connector
import io 
import base64
import datetime
import random
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key' #important to store user session

# Database Creation
def db_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='arya1234',
    )
    c = conn.cursor()
    query = "CREATE DATABASE IF NOT EXISTS testgrocerystore"
    c.execute(query)
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='arya1234',
        database="testgrocerystore"
    )
    c = conn.cursor()
    
    # Creation of tables
    #admin table
    c.execute('''CREATE TABLE admins (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    adusername VARCHAR(255) UNIQUE NOT NULL,
                    adpass VARCHAR(255) NOT NULL,
                    fullname VARCHAR(255) NOT NULL,
                    role VARCHAR(50) NOT NULL DEFAULT 'admin')''')
    #employee table
    c.execute('''CREATE TABLE IF NOT EXISTS employees(
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    empusername VARCHAR(255) NOT NULL UNIQUE,
                    emppassword VARCHAR(255) NOT NULL,
                    empname VARCHAR(255) NOT NULL,
                    role VARCHAR(50) NOT NULL DEFAULT 'employee')''')
    #products table
    c.execute('''CREATE TABLE IF NOT EXISTS products (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    category VARCHAR(255) NOT NULL,
                    price DECIMAL(10, 2) NOT NULL,
                    stock INT NOT NULL,
                    cost_price DECIMAL(10, 2) NOT NULL DEFAULT 0
                )''')
    #sales table
    c.execute('''CREATE TABLE IF NOT EXISTS sales (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    product_id INT NOT NULL,
                    quantity INT NOT NULL,
                    total_price DECIMAL(10, 2) NOT NULL,
                    date_of_sale DATETIME NOT NULL,
                    custName VARCHAR(50) NOT NULL,
                    custphone INT NOT NULL,
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )''')
    
    conn.commit()
    conn.close()

#  User Authentication Registration and Login
def admin_registration(adusername,adpass,fullname):
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='arya1234',
        database='testgrocerystore'
    )
    c=conn.cursor()
    c.execute("INSERT INTO admins (adusername, adpass, fullname) VALUES (%s, %s, %s)", (adusername, adpass, fullname))
    conn.commit()
    conn.close()
    return True
    

def emp_registration(empusername,emppassword,empname):
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='arya1234',
        database='testgrocerystore'
    )
    c=conn.cursor()
    c.execute("INSERT INTO employees(empusername,emppassword,empname)VALUES (%s,%s,%s)",(empusername,emppassword,empname))
    conn.commit()
    conn.close()
    return True
    
    

def admin_login(adusername, adpass):
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='arya1234',
            database='testgrocerystore'
        )
        c = conn.cursor()
        #fetch the data from the database and check admin credentials
        c.execute("SELECT * FROM admins WHERE adusername = %s AND adpass = %s", (adusername, adpass))
        admin = c.fetchone()
        conn.close()
        return admin

def emp_login(empusername, emppassword):
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='arya1234',
            database='testgrocerystore'
        )
        c = conn.cursor()
        # fetch data from the database and validate employee credentials
        c.execute("SELECT * FROM employees WHERE empusername = %s AND emppassword = %s", (empusername, emppassword))
        employee = c.fetchone()
        conn.close()
        return employee

#  Product Management
#get all the products from database
def get_products():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='arya1234',
        database='testgrocerystore'
    )
    c = conn.cursor()
    c.execute("SELECT * FROM products")
    products = c.fetchall()
    conn.close()
    return products
#adding the product details into the database
def add_product(name, category, price, stock, cost_price):
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='arya1234',
        database='testgrocerystore'
    )
    c = conn.cursor()
    c.execute("INSERT INTO products (name, category, price, stock, cost_price) VALUES (%s, %s, %s, %s, %s)",
              (name, category, price, stock, cost_price))
    conn.commit()
    conn.close()
#updating the products if any in the database
def update_product(product_id, name, category, price, stock, cost_price):
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='arya1234',
        database='testgrocerystore'
    )
    c = conn.cursor()
    c.execute("UPDATE products SET name = %s, category = %s, price = %s, stock = %s, cost_price = %s WHERE id = %s",
              (name, category, price, stock, cost_price, product_id))
    conn.commit()
    conn.close()

#deleting the products
def delete_product(product_id):
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='arya1234',
        database='testgrocerystore'
    )
    c = conn.cursor()
    c.execute("DELETE FROM products WHERE id = %s", (product_id,))
    conn.commit()
    conn.close()

# Sales Management 
#recording sales and updating the stock levels after very transaction
def record_sale(product_id, quantity, total_price,custName,custphone,bill_id):
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='arya1234',
        database='testgrocerystore'
    )
    c = conn.cursor()
    c.execute("SELECT stock FROM products WHERE id=%s",(product_id,))
    product=c.fetchone()
    if product and product[0]>=quantity:
        date_of_sale = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("""INSERT INTO sales (product_id, quantity, total_price, date_of_sale, custName, custphone, bill_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        , (product_id, quantity, total_price, date_of_sale, custName, custphone, bill_id))
        c.execute("UPDATE products SET stock = stock - %s WHERE id = %s", (quantity, product_id))
        conn.commit()
        conn.close()
        return True  #sale is successful
    else:
        conn.close()
        return False #sale is failed due to low stocks  
    
#fetching data for monthly reports  
def monthly_reports():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='arya1234',
        database='testgrocerystore'
    )
    c = conn.cursor()
    c.execute("""
    SELECT DATE_FORMAT(date_of_sale, '%Y-%m') AS month, SUM(total_price) AS total_sales
    FROM sales
    GROUP BY month
    ORDER BY month;
    """)
    data = c.fetchall()
    conn.close()
    return data
#fething data to generate sales report along wiht profits
def get_sales_report_with_profit():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='arya1234',
        database='testgrocerystore'
    )
    c = conn.cursor()
    c.execute('''SELECT products.name, SUM(sales.quantity) AS total_quantity, SUM(sales.total_price) AS total_sales,
              SUM(sales.quantity * products.cost_price) as total_cost,
              SUM(sales.total_price -(sales.quantity*products.cost_price)) AS total_profit
            FROM sales
            JOIN products ON sales.product_id = products.id
            GROUP BY sales.product_id
            ORDER BY total_sales DESC''')
    report = c.fetchall()
    conn.close()
    return report


# Routes 
#Home route
@app.route('/')
def home():
    return render_template('index.html')
#Registration Route
@app.route('/admin_registration', methods=['GET', 'POST'])
def admin_reg_page():
    if request.method=='POST':
        adusername=request.form['adusername']
        adpass=request.form['adpass']
        fullname=request.form['fullname']
        result=admin_registration(adusername,adpass,fullname)
        if result:
            flash("Admin registered successfully")
        else:
            flash("Unsuccessful registration!!")
    return render_template('admin_registration.html')
#Admin Login route
@app.route('/admin_login',methods=['GET','POST'])
def admin_login_page():
    if request.method=='POST':
        adusername=request.form['adusername']
        adpass=request.form['adpass']
        admin=admin_login(adusername,adpass)
        if admin:
            return redirect(url_for('admin_dashboard_route'))
        else:
            flash('Invalid Login Credentials!','error')
    return render_template('admin_login.html')

@app.route('/employee_registration', methods=['GET', 'POST'])
def emp_reg_page():
    if request.method=='POST':
        empusername=request.form['empusername']
        emppassword=request.form['emppassword']
        empname=request.form['empname']
        result1=emp_registration(empusername,emppassword,empname)
        if result1:
            flash("Employee registered successfully")
        else:
            flash("Unsuccessful registration!!")
    return render_template('employee_registration.html')

@app.route('/emp_login',methods=['GET','POST'])
def emp_login_page():
    if request.method=='POST':
        empusername=request.form['empusername']
        emppassword=request.form['emppassword']
        employee=emp_login(empusername,emppassword)
        if employee:
            return redirect(url_for('employee_dashboard_route'))
        else:
            flash('Invalid Login Credentials!','error')
    return render_template('emp_login.html')

#logout route
@app.route('/logout')
def logout():
    return redirect(url_for('home'))  # redirect to homepage
    
## Dashboards for admin and employee ###
@app.route('/employee_dashboard')
def employee_dashboard_route():
    # Fetching products grouped by category
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='arya1234',
        database='testgrocerystore'
    )
    c=conn.cursor()
    c.execute("SELECT DISTINCT category FROM products")
    categories = c.fetchall()

    products_by_category = {}

    for category in categories:
        c.execute("SELECT * FROM products WHERE category = %s", (category[0],))
        products = c.fetchall()
        products_by_category[category[0]] = products

    conn.close()

    # Pass the data to the template
    return render_template('employee_dashboard.html', 
                           products_by_category=products_by_category)

@app.route('/admin_dashboard')
def admin_dashboard_route():   
    
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='arya1234',
        database='testgrocerystore'
    )
    c = conn.cursor()
    c.execute("SELECT DISTINCT category FROM products")
    categories = c.fetchall()

    products_by_category = {}
    low_stock_alerts=False #flag to track if stock low

    for category in categories:
        c.execute("SELECT * FROM products WHERE category = %s", (category[0],))
        products = c.fetchall() #this retrieves a list of tuples of products in the database
        products_by_category[category[0]] = products

        #check for low stcok
        for product in products:
            if len(product) > 4 and product[4] < 10: 
                low_stock_alerts=True  #flags stock is low

    conn.close()
    # Render the admin dashboard 
    return render_template('admin_dashboard.html', 
                            products_by_category=products_by_category,
                            low_stock_alerts=low_stock_alerts)  # Pass flag for admin


# Admin Routes for add,update,delete products
@app.route('/add_product', methods=['GET', 'POST'])
def add_product_route():
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        price = float(request.form['price'])
        cost_price = float(request.form['cost_price'])
        stock = int(request.form['stock'])
        add_product(name, category, price, stock, cost_price)
        flash('Product added successfully!')
        return redirect(url_for('add_product_route'))  # to Reload the page after product addition
    
    return render_template('add_product.html')

@app.route('/update_product/<int:product_id>', methods=['GET', 'POST'])
def update_product_route(product_id):
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        price = float(request.form['price'])
        cost_price = float(request.form['cost_price'])
        stock = int(request.form['stock'])
        update_product(product_id, name, category, price, stock, cost_price)
        flash('Product updated successfully!')
        return redirect(url_for('admin_dashboard_route'))

    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='arya1234',
        database='testgrocerystore'
    )
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = c.fetchone()
    conn.close()
    return render_template('update_product.html', product=product)

@app.route('/delete_product/<int:product_id>', methods=['GET', 'POST'])
def delete_product_route(product_id):
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='arya1234',
        database='testgrocerystore'
    )
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = c.fetchone()

    if not product:
        flash("Product not found!")
        return redirect(url_for('admin_dashboard_route'))

    if request.method == 'POST':
        c.execute("SELECT COUNT(*) FROM sales WHERE product_id = %s", (product_id,))
        related_sales = c.fetchone()[0]

        if related_sales > 0:
            flash("Cannot delete product. It has related sales records.")
            return redirect(url_for('admin_dashboard_route'))

        c.execute("DELETE FROM products WHERE id = %s", (product_id,))
        conn.commit()
        flash(f"Product '{product[1]}' deleted successfully!")
        return redirect(url_for('admin_dashboard_route'))

    return render_template('confirm_delete.html', product=product)


@app.route('/sales_report')
def sales_report():
    data = monthly_reports()
    months = [row[0] for row in data]
    sales = [float(row[1]) for row in data]
    is_increasing = all(sales[i] <= sales[i+1] for i in range(len(sales)-1))
    is_decreasing = all(sales[i] >= sales[i+1] for i in range(len(sales)-1))

    plt.figure(figsize=(10, 6))
    plt.plot(months, sales, marker='o', color='b' if is_increasing else 'r', label='Sales')
    plt.title('Monthly Sales Report')
    plt.xlabel('Month')
    plt.ylabel('Total Sales')
    plt.xticks(rotation=45)
    plt.grid()
    plt.legend()
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    line_graph_data = base64.b64encode(img.getvalue()).decode()

    report = get_sales_report_with_profit()
    total_sales = sum(row[2] for row in report)
    labels = [item[0] for item in report]
    sales = [float(item[2]) for item in report]
    profits = [float(item[4]) for item in report]

    fig_pie, ax_pie = plt.subplots()
    ax_pie.pie(sales, labels=labels, autopct='%1.1f%%', startangle=140)
    ax_pie.axis('equal')
    pie_img = io.BytesIO()
    plt.savefig(pie_img, format='png')
    pie_img.seek(0)
    pie_chart_data = base64.b64encode(pie_img.getvalue()).decode('utf-8')
    plt.close(fig_pie)

    fig_bar, ax_bar = plt.subplots()
    x = range(len(labels))
    ax_bar.bar(x, sales, label='Sales (₹)', alpha=0.7, color='blue')
    ax_bar.bar(x, profits, label='Profit (₹)', alpha=0.7, color='green')
    ax_bar.set_xticks(x)
    ax_bar.set_xticklabels(labels, rotation=45, ha='right')
    ax_bar.set_ylabel('Amount (₹)')
    ax_bar.set_title('Sales and Profit Comparison')
    ax_bar.legend()
    bar_img = io.BytesIO()
    plt.tight_layout()
    plt.savefig(bar_img, format='png')
    bar_img.seek(0)
    bar_chart_data = base64.b64encode(bar_img.getvalue()).decode('utf-8')
    plt.close(fig_bar)

    img = io.BytesIO()
    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')

    return render_template('sales_report.html', 
                           report=report, 
                           data=data,
                           total_sales=total_sales,
                           pie_chart_data=pie_chart_data,
                           bar_chart_data=bar_chart_data,
                           line_graph_data=line_graph_data,
                           img_data=img_base64)


def calculate_total(cart):
    total = 0
    for item in cart:
        total += float(item['total_price'])
    return total

@app.route('/remove-from-cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    if 'cart' in session:
        cart = session['cart']
        session['cart'] = [item for item in cart if item['id'] != product_id]
        session.modified = True
    return redirect(url_for('invoice'))


@app.route('/billing', methods=['GET', 'POST'])
def billing():
    if 'cart' not in session:
        session['cart'] = []
    if "checkout_done" in session:
        session.pop("cart", None)
        session.pop("checkout_done", None)

    if request.method == 'POST':
        if "add_to_cart" in request.form:
            product_id = int(request.form['product_id'])
            quantity = int(request.form['quantity'])

            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='arya1234',
                database='testgrocerystore'
            )
            c = conn.cursor()
            c.execute("SELECT * FROM products WHERE id = %s", (product_id,))
            product = c.fetchone()
            conn.close()

            if product:
                available_stock = product[4]
                if 0 < quantity <= available_stock:
                    cart_item = {
                        "id": product[0],
                        "name": product[1],
                        "category": product[2],
                        "price": float(product[3]),
                        "quantity": quantity,
                        "total_price": float(product[3]) * quantity
                    }
                    session['cart'].append(cart_item)
                    session.modified = True
                    flash(f"{product[1]} added to the cart.")
                elif quantity > available_stock:
                    flash(f"Not enough stock for {product[1]}. Available stock: {available_stock}")
                else:
                    flash("Invalid quantity selected.")
            else:
                flash("Product not found!")
        return redirect(url_for("billing"))

    cart = session.get('cart', [])
    total = calculate_total(cart)
    products = get_products()
    return render_template('billing.html', products=products, cart=cart, total=total)


@app.route('/checkout', methods=['POST'])
def checkout():
    cart = session.get('cart', [])
    custName = request.form['custName']
    custphone = request.form['custphone']

    if not custName or not custphone:
        flash("Customer details are required for checkout!")
        return redirect(url_for('billing'))

    bill_id = generate_bill_id()

    for item in cart:
        record_sale(item['id'], item['quantity'], item['total_price'], custName, custphone, bill_id)

    session['bill_id'] = bill_id
    session['custName'] = custName
    session['custphone'] = custphone
    session['checkout_done'] = True
    return redirect(url_for('invoice'))

def generate_bill_id():
    timestamp = int(time.time())
    random_number = random.randint(1000, 9999)
    bill_id = f"INV-{timestamp}-{random_number}"
    return bill_id


@app.route('/invoice', methods=['GET'])
def invoice():
    if 'checkout_done' not in session or not session['checkout_done']:
        flash("No recent checkout found. Please complete your purchase first.")
        return redirect(url_for('billing'))

    cart = session.get('cart', [])
    if not cart:
        flash("Your cart is empty!")
        return redirect(url_for('billing'))
    bill_id = session.get('bill_id')

    total = calculate_total(cart)
    response = render_template('invoice.html', cart=cart, total=total, bill_id=bill_id)

    session.pop('cart', None)
    session.pop('checkout_done', None)
    session.pop('bill_id', None)
    return response


@app.route('/view_purchases', methods=['GET'])
def view_purchases():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='arya1234',
        database='testgrocerystore'
    )
    c = conn.cursor(dictionary=True)
    search_element = request.args.get('search', '')
    if search_element:
        search_element = f'%{search_element.lower()}%'
        c.execute("""
            SELECT bill_id, custName, custPhone, product_id, quantity, total_price, date_of_sale
            FROM sales
            WHERE LOWER(bill_id) LIKE %s
            OR LOWER(custName) LIKE %s
            OR LOWER(product_id) LIKE %s
            ORDER BY date_of_sale DESC
        """, (search_element, search_element, search_element))
        sales = c.fetchall()
        if not sales:
            return redirect(url_for('view_purchases'))
    else:
        c.execute("""
            SELECT bill_id, custName, custPhone, product_id, quantity, total_price, date_of_sale
            FROM sales
            ORDER BY date_of_sale DESC
        """)
        sales = c.fetchall()
    conn.close()
    return render_template('view_purchases.html', sales=sales)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
