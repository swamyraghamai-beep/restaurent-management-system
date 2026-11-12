import os
import re
import json
import uuid
import requests

from dotenv import load_dotenv

from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key-in-env")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024


# =====================================================
# DATABASE CONNECTION
# =====================================================



def get_db_connection():
    """Connect to the Aiven MySQL database using values from .env / Render."""
    required_vars = ["MYSQLHOST", "MYSQLUSER", "MYSQLPASSWORD"]

    missing = [
        name for name in required_vars
        if not os.environ.get(name)
    ]

    if missing:
        raise RuntimeError(
            "Missing database environment variables: " + ", ".join(missing)
        )

    db_config = {
        "host": os.environ["MYSQLHOST"].strip(),
        "port": int(os.environ.get("MYSQLPORT", "13571")),
        "user": os.environ["MYSQLUSER"].strip(),
        "password": os.environ["MYSQLPASSWORD"],
        "database": os.environ.get("MYSQLDATABASE", "restaurantdb").strip(),
        "connection_timeout": 15,
    }

    # Locally use MYSQLSSLCA=ca.pem. On Render use
    # MYSQLSSLCA=/etc/secrets/ca.pem.
    ssl_ca = os.environ.get("MYSQLSSLCA", "").strip()

    if ssl_ca:
        if not os.path.isabs(ssl_ca):
            ssl_ca = os.path.join(BASE_DIR, ssl_ca)

        if not os.path.isfile(ssl_ca):
            raise FileNotFoundError(
                f"MySQL CA certificate was not found: {ssl_ca}"
            )

        db_config.update({
            "ssl_ca": ssl_ca,
            "ssl_verify_cert": True,
            "ssl_verify_identity": True,
        })

    return mysql.connector.connect(**db_config)


# =====================================================
# FOOD PHOTOS
# =====================================================

# Uploaded menu photos are saved as real files in this folder.
# On Railway, mount a persistent volume at this exact folder path.
FOOD_IMAGE_FOLDER = os.path.join(app.static_folder, "images", "food")
os.makedirs(FOOD_IMAGE_FOLDER, exist_ok=True)


def get_food_image(item_name, force_refresh=False):
    """Never guess a food photo. Use the Change Photo upload instead."""
    return None


def get_food_image_credit(filename):

    if not filename:
        return None

    credit_path = os.path.join(
        FOOD_IMAGE_FOLDER,
        filename + ".credit.json"
    )

    try:
        with open(
            credit_path, "r", encoding="utf-8"
        ) as credit_file:

            return json.load(credit_file)

    except (OSError, ValueError):
        return None


# =====================================================
# HOME
# =====================================================

@app.route("/")
def home():
    return redirect(url_for("login"))


# =====================================================
# STAFF REGISTRATION
# =====================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        full_name = request.form.get(
            "full_name", ""
        ).strip()

        email = request.form.get(
            "email", ""
        ).strip().lower()

        phone = request.form.get(
            "phone", ""
        ).strip()

        password = request.form.get("password", "")

        confirm_password = request.form.get(
            "confirm_password", ""
        )

        if not all([
            full_name,
            email,
            phone,
            password,
            confirm_password
        ]):

            return render_template(
                "register.html",
                error="Please fill in all fields."
            )

        if password != confirm_password:

            return render_template(
                "register.html",
                error="Passwords do not match."
            )

        if len(password) < 8:

            return render_template(
                "register.html",
                error="Password must contain at least 8 characters."
            )

        db = get_db_connection()
        cursor = db.cursor()

        try:

            cursor.execute(
                "SELECT COUNT(*) FROM users"
            )

            user_count = cursor.fetchone()[0]

            role = (
                "Admin" if user_count == 0
                else "Staff"
            )

            password_hash = generate_password_hash(
                password
            )

            cursor.execute("""
                INSERT INTO users
                (full_name, email, phone, password_hash, role)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                full_name,
                email,
                phone,
                password_hash,
                role
            ))

            db.commit()

            return redirect(url_for(
                "login",
                message="Registration successful! Please log in."
            ))

        except mysql.connector.IntegrityError:

            db.rollback()

            return render_template(
                "register.html",
                error="This email is already registered."
            )

        except mysql.connector.Error as error:

            db.rollback()

            return render_template(
                "register.html",
                error=f"Registration error: {error}"
            )

        finally:
            cursor.close()
            db.close()

    return render_template("register.html")


# =====================================================
# LOGIN
# =====================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    message = request.args.get("message", "")

    if request.method == "POST":

        email = (
            request.form.get("email")
            or request.form.get("username")
            or ""
        ).strip().lower()

        password = request.form.get("password", "")

        db = get_db_connection()
        cursor = db.cursor()

        try:

            cursor.execute("""
                SELECT user_id, full_name, email,
                       password_hash, role
                FROM users
                WHERE email = %s
            """, (email,))

            user = cursor.fetchone()

            if user and check_password_hash(
                user[3], password
            ):

                session.clear()

                session["user_id"] = user[0]
                session["user"] = user[2]
                session["full_name"] = user[1]
                session["role"] = user[4]

                return redirect(url_for("dashboard"))

            return render_template(
                "login.html",
                error="Invalid email or password.",
                message=message
            )

        except mysql.connector.Error as error:

            return render_template(
                "login.html",
                error=f"Login error: {error}",
                message=message
            )

        finally:
            cursor.close()
            db.close()

    return render_template(
        "login.html",
        message=message
    )


# =====================================================
# DASHBOARD
# =====================================================

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("dashboard.html")


# =====================================================
# LOGOUT
# =====================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# =====================================================
# CUSTOMER MANAGEMENT
# =====================================================

@app.route("/customers", methods=["GET", "POST"])
def customers():

    if "user" not in session:
        return redirect(url_for("login"))

    db = get_db_connection()
    cursor = db.cursor()

    try:

        if request.method == "POST":

            name = request.form.get("customer_name")
            phone = request.form.get("phone")
            email = request.form.get("email")

            cursor.execute("""
                INSERT INTO `Customers`
                (customer_name, phone, email)
                VALUES (%s, %s, %s)
            """, (name, phone, email))

            db.commit()

        cursor.execute(
            "SELECT * FROM `Customers`"
        )

        customer_list = cursor.fetchall()

        return render_template(
            "customers.html",
            customers=customer_list
        )

    finally:
        cursor.close()
        db.close()


# =====================================================
# MENU MANAGEMENT
# =====================================================

@app.route("/menu", methods=["GET", "POST"])
def menu():

    if "user" not in session:
        return redirect(url_for("login"))

    db = get_db_connection()
    cursor = db.cursor()

    message = ""
    error = ""

    try:

        # ADD NEW FOOD ITEM
        if request.method == "POST":

            item_name = request.form.get(
                "item_name", ""
            ).strip()

            category_id = request.form.get(
                "category_id"
            )

            description = request.form.get(
                "description", ""
            ).strip()

            price_value = request.form.get("price")

            available_value = request.form.get(
                "available", "1"
            )

            if not item_name or not category_id or not price_value:
                raise ValueError(
                    "Please fill in all required fields."
                )

            try:

                category_id = int(category_id)
                price = float(price_value)

            except (TypeError, ValueError):

                raise ValueError(
                    "Please select a valid category and enter a valid price."
                )

            if price <= 0:
                raise ValueError(
                    "Price must be greater than zero."
                )

            if available_value not in ("0", "1"):
                raise ValueError(
                    "Invalid availability selection."
                )

            # CHECK CATEGORY
            cursor.execute("""
                SELECT category_id
                FROM `Categories`
                WHERE category_id = %s
            """, (category_id,))

            if not cursor.fetchone():
                raise ValueError(
                    "Please select a valid category."
                )

            # AUTOMATIC PHOTO SEARCH
            image_filename = get_food_image(item_name)

            # INSERT FOOD ITEM
            cursor.execute("""
                INSERT INTO `MenuItems`
                (
                    item_name,
                    category_id,
                    description,
                    price,
                    available,
                    image_filename
                )
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                item_name,
                category_id,
                description,
                price,
                int(available_value),
                image_filename
            ))

            db.commit()

            if image_filename:

                message = (
                    "Food item added successfully with an "
                    "automatically matched photograph."
                )

            else:

                message = (
                    "Food item added successfully, but no matching "
                    "photograph was found. Please use Add Photo."
                )

        # GET CATEGORIES
        cursor.execute("""
            SELECT category_id, category_name
            FROM `Categories`
            ORDER BY category_name
        """)

        categories = cursor.fetchall()

        # GET FOOD ITEMS
        cursor.execute("""
            SELECT
                m.item_id,
                m.item_name,
                c.category_name,
                m.description,
                m.price,
                m.available,
                m.image_filename
            FROM `MenuItems` m
            LEFT JOIN `Categories` c
                ON m.category_id = c.category_id
            ORDER BY m.item_id DESC
        """)

        menu_items = cursor.fetchall()

        # SEARCH PHOTOS FOR EXISTING ITEMS
        changed = False

        for item in menu_items:

            if not item[6]:

                filename = get_food_image(item[1])

                if filename:

                    cursor.execute("""
                        UPDATE `MenuItems`
                        SET image_filename = %s
                        WHERE item_id = %s
                          AND (
                              image_filename IS NULL
                              OR image_filename = ''
                          )
                    """, (
                        filename,
                        item[0]
                    ))

                    changed = True

        if changed:

            db.commit()

            cursor.execute("""
                SELECT
                    m.item_id,
                    m.item_name,
                    c.category_name,
                    m.description,
                    m.price,
                    m.available,
                    m.image_filename
                FROM `MenuItems` m
                LEFT JOIN `Categories` c
                    ON m.category_id = c.category_id
                ORDER BY m.item_id DESC
            """)

            menu_items = cursor.fetchall()

        image_credits = {
            item[6]: get_food_image_credit(item[6])
            for item in menu_items
            if item[6]
        }

        return render_template(
            "menu.html",
            categories=categories,
            menu_items=menu_items,
            message=message,
            error=error,
            image_credits=image_credits
        )

    except (mysql.connector.Error, ValueError) as e:

        db.rollback()
        error = str(e)

        cursor.execute("""
            SELECT category_id, category_name
            FROM `Categories`
            ORDER BY category_name
        """)

        categories = cursor.fetchall()

        cursor.execute("""
            SELECT
                m.item_id,
                m.item_name,
                c.category_name,
                m.description,
                m.price,
                m.available,
                m.image_filename
            FROM `MenuItems` m
            LEFT JOIN `Categories` c
                ON m.category_id = c.category_id
            ORDER BY m.item_id DESC
        """)

        menu_items = cursor.fetchall()

        image_credits = {
            item[6]: get_food_image_credit(item[6])
            for item in menu_items
            if item[6]
        }

        return render_template(
            "menu.html",
            categories=categories,
            menu_items=menu_items,
            message=message,
            error=error,
            image_credits=image_credits
        )

    finally:
        cursor.close()
        db.close()


# =====================================================
# PHOTO REFRESH (NO AUTOMATIC REPLACEMENT)
# =====================================================

@app.route("/menu/refresh-images", methods=["POST"])
def refresh_food_images():
    if "user" not in session:
        return redirect(url_for("login"))

    # Keep every photo already selected by the user. Do not replace it
    # with an automatically guessed image.
    return redirect(url_for(
        "menu",
        message="Your selected food photos have been kept. Use Change Photo to update an image."
    ))

# =====================================================
# UPLOAD OR CHANGE FOOD PHOTOGRAPH
# =====================================================

@app.route("/menu/upload-image/<int:item_id>", methods=["POST"])
def upload_food_image(item_id):

    if "user" not in session:
        return redirect(url_for("login"))

    image = request.files.get("food_image")

    if not image or not image.filename:
        return redirect(url_for("menu"))

    allowed_extensions = {
        "jpg", "jpeg", "png", "webp"
    }

    original_name = secure_filename(image.filename)

    if "." not in original_name:
        return "Invalid image file.", 400

    extension = original_name.rsplit(".", 1)[1].lower()

    if extension not in allowed_extensions:

        return (
            "Only JPG, JPEG, PNG and WEBP images are allowed.",
            400
        )

    filename = (
        f"food_{item_id}_{uuid.uuid4().hex[:10]}.{extension}"
    )

    image_folder = FOOD_IMAGE_FOLDER
    os.makedirs(image_folder, exist_ok=True)

    image_path = os.path.join(
        image_folder, filename
    )

    db = get_db_connection()
    cursor = db.cursor()

    try:

        cursor.execute(
            "SELECT image_filename FROM `MenuItems` WHERE item_id = %s",
            (item_id,)
        )

        item = cursor.fetchone()

        if not item:
            return "Food item not found.", 404

        image.save(image_path)

        cursor.execute("""
            UPDATE `MenuItems`
            SET image_filename = %s
            WHERE item_id = %s
        """, (filename, item_id))

        db.commit()

        old_filename = item[0]

        if old_filename and old_filename != filename:

            old_path = os.path.abspath(
                os.path.join(image_folder, old_filename)
            )

            if (
                os.path.dirname(old_path)
                == os.path.abspath(image_folder)
                and os.path.isfile(old_path)
            ):

                os.remove(old_path)

        return redirect(url_for("menu"))

    except Exception:

        db.rollback()

        if os.path.isfile(image_path):
            os.remove(image_path)

        raise

    finally:
        cursor.close()
        db.close()


# =====================================================
# ORDER MANAGEMENT
# =====================================================

@app.route("/orders", methods=["GET", "POST"])
def orders():

    if "user" not in session:
        return redirect(url_for("login"))

    message = request.args.get("message", "")

    db = get_db_connection()
    cursor = db.cursor()

    try:

        # PLACE NEW ORDER
        if request.method == "POST":

            customer_id = request.form.get("customer_id")
            table_id = request.form.get("table_id")
            order_type = request.form.get("order_type")

            item_ids = request.form.getlist("item_id[]")
            quantities = request.form.getlist("quantity[]")

            if not customer_id or not order_type or not item_ids:

                message = (
                    "Please select a customer and at least one food item."
                )

            elif order_type not in [
                "Dine-in",
                "Takeaway",
                "Delivery"
            ]:

                message = "Invalid order type."

            elif order_type == "Dine-in" and not table_id:

                message = "Please select a table for Dine-in."

            else:

                selected_items = {}

                for item_id, quantity in zip(
                    item_ids, quantities
                ):

                    item_id = int(item_id)
                    quantity = int(quantity)

                    if quantity < 1:
                        raise ValueError(
                            "Quantity must be at least 1."
                        )

                    selected_items[item_id] = (
                        selected_items.get(item_id, 0) + quantity
                    )

                if not selected_items:
                    raise ValueError(
                        "Please select at least one food item."
                    )

                selected_table = (
                    int(table_id)
                    if order_type == "Dine-in"
                    else None
                )

                # GET EMPLOYEE ID
                cursor.execute(
                    "SELECT MIN(employee_id) FROM `Employees`"
                )

                employee_result = cursor.fetchone()
                employee_id = employee_result[0]

                if employee_id is None:
                    raise ValueError(
                        "Please add an employee before placing an order."
                    )

                order_items = []

                for item_id, quantity in selected_items.items():

                    cursor.execute("""
                        SELECT item_name, price
                        FROM `MenuItems`
                        WHERE item_id = %s
                          AND available = TRUE
                    """, (item_id,))

                    food = cursor.fetchone()

                    if food is None:
                        raise ValueError(
                            "One of the selected food items is unavailable."
                        )

                    order_items.append((
                        item_id,
                        quantity,
                        food[1]
                    ))

                # CREATE ORDER
                cursor.execute("""
                    INSERT INTO `Orders`
                    (
                        customer_id,
                        table_id,
                        employee_id,
                        order_type,
                        status
                    )
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    int(customer_id),
                    selected_table,
                    employee_id,
                    order_type,
                    "Pending"
                ))

                order_id = cursor.lastrowid

                # SAVE ORDER DETAILS
                for item_id, quantity, price in order_items:

                    cursor.execute("""
                        INSERT INTO `OrderDetails`
                        (
                            order_id,
                            item_id,
                            quantity,
                            unit_price
                        )
                        VALUES (%s, %s, %s, %s)
                    """, (
                        order_id,
                        item_id,
                        quantity,
                        price
                    ))

                # UPDATE TABLE STATUS
                if selected_table is not None:

                    cursor.execute("""
                        UPDATE `RestaurantTables`
                        SET status = 'Occupied'
                        WHERE table_id = %s
                    """, (selected_table,))

                db.commit()

                return redirect(
                    url_for(
                        "orders",
                        message=(
                            "Order placed successfully! Order ID: "
                            + str(order_id)
                        )
                    )
                )

        # GET CUSTOMERS
        cursor.execute("""
            SELECT customer_id, customer_name
            FROM `Customers`
            ORDER BY customer_id
        """)

        customer_list = cursor.fetchall()

        # GET TABLES
        cursor.execute("""
            SELECT table_id, table_number, capacity, status
            FROM `RestaurantTables`
            ORDER BY table_number
        """)

        table_list = cursor.fetchall()

        # GET AVAILABLE FOOD
        cursor.execute("""
            SELECT item_id, item_name, price
            FROM `MenuItems`
            WHERE available = TRUE
            ORDER BY item_name
        """)

        menu_list = cursor.fetchall()

        # GET RECENT ORDERS
        cursor.execute("""
            SELECT order_id, customer_id, order_type, status
            FROM `Orders`
            ORDER BY order_id DESC
        """)

        order_list = cursor.fetchall()

        return render_template(
            "orders.html",
            customers=customer_list,
            tables=table_list,
            menu_items=menu_list,
            orders=order_list,
            message=message
        )

    except (mysql.connector.Error, ValueError) as error:

        db.rollback()

        return f"Order error: {error}", 500

    finally:
        cursor.close()
        db.close()


# =====================================================
# COMPLETE ORDER AND UPDATE TABLE STATUS
# =====================================================

@app.route("/complete_order/<int:order_id>", methods=["POST"])
def complete_order(order_id):

    if "user" not in session:
        return redirect(url_for("login"))

    db = get_db_connection()
    cursor = db.cursor()

    try:

        cursor.execute("""
            SELECT table_id, order_type
            FROM `Orders`
            WHERE order_id = %s
        """, (order_id,))

        order = cursor.fetchone()

        if order is None:
            return "Order not found", 404

        table_id, order_type = order

        cursor.execute("""
            UPDATE `Orders`
            SET status = 'Completed'
            WHERE order_id = %s
        """, (order_id,))

        if order_type == "Dine-in" and table_id is not None:

            cursor.execute("""
                SELECT COUNT(*)
                FROM `Orders`
                WHERE table_id = %s
                  AND order_type = 'Dine-in'
                  AND status IN (
                      'Pending',
                      'Preparing',
                      'Ready'
                  )
                  AND order_id != %s
            """, (
                table_id,
                order_id
            ))

            active_orders = cursor.fetchone()[0]

            if active_orders == 0:

                cursor.execute("""
                    UPDATE `RestaurantTables`
                    SET status = 'Available'
                    WHERE table_id = %s
                """, (table_id,))

        db.commit()

        return redirect(url_for(
            "orders",
            message="Order completed successfully!"
        ))

    except mysql.connector.Error as error:

        db.rollback()

        return f"Error: {error}", 500

    finally:
        cursor.close()
        db.close()


# =====================================================
# PAYMENTS MANAGEMENT
# =====================================================

@app.route("/payments", methods=["GET", "POST"])
def payments():

    if "user" not in session:
        return redirect(url_for("login"))

    db = get_db_connection()
    cursor = db.cursor()

    message = request.args.get("message", "")

    try:

        if request.method == "POST":

            order_id = request.form.get("order_id")

            payment_method = request.form.get(
                "payment_method"
            )

            allowed_methods = [
                "Cash",
                "UPI",
                "Card",
                "Online"
            ]

            if (
                not order_id
                or payment_method not in allowed_methods
            ):

                message = (
                    "Please select an order and payment method."
                )

            else:

                order_id = int(order_id)

                # CALCULATE ORDER AMOUNT
                cursor.execute("""
                    SELECT COALESCE(
                        SUM(quantity * unit_price), 0
                    )
                    FROM `OrderDetails`
                    WHERE order_id = %s
                """, (order_id,))

                amount = cursor.fetchone()[0]

                if amount <= 0:

                    message = "No valid order amount found."

                else:

                    # CHECK EXISTING PAYMENT
                    cursor.execute("""
                        SELECT payment_id, payment_status
                        FROM `Payments`
                        WHERE order_id = %s
                    """, (order_id,))

                    existing_payment = cursor.fetchone()

                    if existing_payment:

                        payment_id, payment_status = existing_payment

                        if payment_status == "Paid":

                            message = (
                                "This order has already been paid."
                            )

                        elif payment_status in (
                            "Pending",
                            "Failed"
                        ):

                            cursor.execute("""
                                UPDATE `Payments`
                                SET amount = %s,
                                    payment_method = %s,
                                    payment_status = 'Paid',
                                    payment_date = CURRENT_TIMESTAMP
                                WHERE payment_id = %s
                            """, (
                                amount,
                                payment_method,
                                payment_id
                            ))

                            db.commit()

                            return redirect(url_for(
                                "payments",
                                message=(
                                    "Pending payment completed successfully!"
                                )
                            ))

                        else:

                            message = (
                                "This payment cannot be processed."
                            )

                    else:

                        cursor.execute("""
                            INSERT INTO `Payments`
                            (
                                order_id,
                                amount,
                                payment_method,
                                payment_status,
                                payment_date
                            )
                            VALUES (
                                %s,
                                %s,
                                %s,
                                'Paid',
                                CURRENT_TIMESTAMP
                            )
                        """, (
                            order_id,
                            amount,
                            payment_method
                        ))

                        db.commit()

                        return redirect(url_for(
                            "payments",
                            message="Payment completed successfully!"
                        ))

        # GET UNPAID ORDERS
        cursor.execute("""
            SELECT
                o.order_id,
                COALESCE(
                    SUM(od.quantity * od.unit_price), 0
                )
            FROM `Orders` o
            JOIN `OrderDetails` od
                ON o.order_id = od.order_id
            LEFT JOIN `Payments` p
                ON o.order_id = p.order_id
            WHERE p.payment_id IS NULL
               OR p.payment_status IN ('Pending', 'Failed')
            GROUP BY o.order_id
            ORDER BY o.order_id DESC
        """)

        unpaid_orders = cursor.fetchall()

        # PAYMENT HISTORY
        cursor.execute("""
            SELECT
                payment_id,
                order_id,
                amount,
                payment_method,
                payment_status,
                payment_date
            FROM `Payments`
            ORDER BY payment_id DESC
        """)

        payment_history = cursor.fetchall()

        return render_template(
            "payments.html",
            unpaid_orders=unpaid_orders,
            payment_history=payment_history,
            message=message
        )

    except (mysql.connector.Error, ValueError) as error:

        db.rollback()

        return f"Payment error: {error}", 500

    finally:
        cursor.close()
        db.close()


# =====================================================
# RUN APPLICATION
# =====================================================

if __name__ == "__main__":
    app.run(debug=True)