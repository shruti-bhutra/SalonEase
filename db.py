import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

DB_NAME = "salonease.db"

# ===================================================
# CONNECT DATABASE
# ===================================================
def connect_db():

    conn = sqlite3.connect(
        DB_NAME,
        timeout=30,
        check_same_thread=False
    )

    conn.execute("PRAGMA journal_mode=WAL")

    return conn
# ===================================================
# CREATE TABLES
# ===================================================

def create_tables():

    conn = connect_db()
    cursor = conn.cursor()

    # USERS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        gender TEXT
    )
    """)

    # APPOINTMENTS TABLE
    cursor.execute('''
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    service TEXT,
    date TEXT,
    time TEXT,
    payment TEXT,
    status TEXT DEFAULT 'Pending'
                   
)
''')

    # ADMIN TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)
# SERVICES TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS services(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    price TEXT,
    category TEXT,
    image TEXT
)
""")
    conn.commit()
    conn.close()
# ===================================================
# REGISTER USER
# ===================================================

def register_user(name, email, password, gender):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email=?",
        (email,)
    )

    existing_user = cursor.fetchone()

    if existing_user:
        conn.close()
        return False

    cursor.execute("""
    INSERT INTO users(name, email, password, gender)
    VALUES (?, ?, ?, ?)
    """, (name, email, password, gender))

    conn.commit()
    conn.close()

    return True

# ===================================================
# LOGIN USER
# ===================================================

def login_user(email, password):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email, password)
    )

    user = cursor.fetchone()

    conn.close()

    return user

# ===================================================
# UPDATE USER
# ===================================================

def update_user(name, email, gender, old_email):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE users
    SET name=?, email=?, gender=?
    WHERE email=?
    """, (name, email, gender, old_email))

    conn.commit()
    conn.close()

# ===================================================
# SAVE APPOINTMENT
# ===================================================
def save_appointment(user_id, service, date, time, payment):

    conn = connect_db()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO appointments
            (user_id, service, date, time, payment)

            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, service, date, time, payment)
        )

        conn.commit()

    finally:

        conn.close()

    return True
# ===================================================
# CREATE DEFAULT ADMIN
# ===================================================

def create_default_admin():

    conn = connect_db()
    cursor = conn.cursor()

    admin_email = "admin@salonease.com"
    admin_password = generate_password_hash("admin123")

    cursor.execute(
        "SELECT * FROM admin WHERE email=?",
        (admin_email,)
    )

    existing_admin = cursor.fetchone()

    if not existing_admin:

        cursor.execute("""
        INSERT INTO admin(email, password)
        VALUES (?, ?)
        """, (admin_email, admin_password))

        conn.commit()

    conn.close()

# ===================================================
# ADMIN LOGIN
# ===================================================

def admin_login(email, password):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM admin WHERE email=?",
        (email,)
    )

    admin = cursor.fetchone()

    conn.close()

    if admin and check_password_hash(admin[2], password):
        return admin

    return None

# ===================================================
# RUN FILE
# ===================================================

if __name__ == "__main__":

    create_tables()
    create_default_admin()

    print("Database & tables created!")
    # ===================================================
# ADD SERVICE
# ===================================================

def add_service(name, price, category, image):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO services(name, price, category, image)
    VALUES (?, ?, ?, ?)
    """, (name, price, category, image))

    conn.commit()
    conn.close()


# ===================================================
# GET ALL SERVICES
# ===================================================

def get_services():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM services")

    services = cursor.fetchall()

    conn.close()

    return services


# ===================================================
# DELETE SERVICE
# ===================================================

def delete_service(service_id):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM services WHERE id=?",
        (service_id,)
    )

    conn.commit()
    conn.close()

# ===================================================
# TOTAL USERS
# ===================================================

def total_users():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM users"
    )

    total = cursor.fetchone()[0]

    conn.close()

    return total


# ===================================================
# TOTAL SERVICES
# ===================================================

def total_services():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM services"
    )

    total = cursor.fetchone()[0]

    conn.close()

    return total


# ===================================================
# TOTAL BOOKINGS
# ===================================================

def total_bookings():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM appointments"
    )

    total = cursor.fetchone()[0]

    conn.close()

    return total


# ===================================================
# RECENT BOOKINGS
# ===================================================

def recent_bookings():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM appointments
    ORDER BY id DESC
    LIMIT 5
    """)

    bookings = cursor.fetchall()

    conn.close()

    return bookings

