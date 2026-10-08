from flask import Flask, render_template, request, redirect, session, url_for, Response 
import sqlite3
import csv
from db import (
    create_tables,
    register_user,
    login_user,
    update_user,
    save_appointment,
    create_default_admin,
    admin_login,
    add_service,
    get_services,
    delete_service,
    total_users,
    total_services,
    total_bookings,
    recent_bookings
)
from flask import send_file
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    PageBreak
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
# ===================================================
# CREATE FLASK APP
# ===================================================
app = Flask(__name__)
app.secret_key = "secret123"

create_tables() 
create_default_admin()
# ===================================================
# CREATE DATABASE TABLES
# ===================================================
# SERVICES DATA
# ===================================================

services_data = {
    "popular": [

        {
            "name": "Hair Spa",
            "price": "₹999"
        },

        {
            "name": "Bridal Package",
            "price": "₹5999"
        },

        {
            "name": "Luxury Groom Package",
            "price": "₹3499"
        }

    ]
}

# ===================================================
# HOME PAGE
# ===================================================

@app.route('/')
def home():

    return render_template('user/index.html')

# ===================================================
# REGISTER PAGE
# ===================================================
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        gender = request.form['gender']

        success = register_user(
            name,
            email,
            password,
            gender
        )

        if success:

            return redirect('/login')

        else:

            return "Email already exists ❌"

    return render_template('user/register.html')
# ===================================================
# LOGIN PAGE
# ===================================================

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        user = login_user(email, password)

        if user:

            # Store user info in session
            session['id'] = user[0]
            session['user'] = user[1]
            session['email'] = user[2]
            session['gender'] = user[4]

            return redirect('/dashboard')

        else:

            return "Invalid Credentials ❌"
    return render_template('user/login.html')

# ===================================================
# DASHBOARD PAGE
# ===================================================

@app.route('/dashboard')
def dashboard():

    # Check login
    if 'user' not in session:

        return redirect('/login')

    return render_template(
        'user/dashboard.html',
        username=session['user']
    )
# ===================================================
# SERVICES PAGE
# ===================================================

@app.route('/services')
def services_page():

    if 'user' not in session:
        return redirect('/login')

    services = get_services()

    return render_template(
        'user/services.html',
        services=services
    )
# ===================================================
# PROFILE PAGE
# ===================================================
@app.route('/profile')
def profile():

    if 'user' not in session:
        return redirect('/login')

    return render_template(
        'user/profile.html',
        username=session['user'],
        email=session['email'],
        gender=session['gender']
    )
# ===================================================
# LOGOUT
# ===================================================

@app.route('/logout')
def logout():

    session.clear()

    return redirect('/')

# ===================================================
# RUN FLASK APP
# ===================================================
# EDIT PROFILE
# ===================================================

@app.route('/edit-profile', methods=['GET', 'POST'])
def edit_profile():

    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':

        new_name = request.form['name']
        new_email = request.form['email']
        new_gender = request.form['gender']

        old_email = session['email']

        update_user(
            new_name,
            new_email,
            new_gender,
            old_email
        )

        # Update session
        session['user'] = new_name
        session['email'] = new_email
        session['gender'] = new_gender

        return redirect('/profile')

    return render_template(
        'user/edit_profile.html',
        username=session['user'],
        email=session['email'],
        gender=session['gender']
    )
# ===================================================
# BOOKING PAGE
# ===================================================

@app.route('/booking', methods=['GET', 'POST'])
def booking():

    if 'user' not in session:
        return redirect('/login')

    # =========================================
    # FORM SUBMIT
    # =========================================

    if request.method == 'POST':

        service = request.form['service']

        price = float(
            request.form['price']
        )

        date = request.form['date']

        time = request.form['time']

        payment = request.form['payment']

        # SAVE TEMP DATA IN SESSION

        session['booking_data'] = {

            'service': service,
            'date': date,
            'time': time,
            'payment': payment

        }

        # =====================================
        # UPI FLOW
        # =====================================

        if payment == "UPI":

            return redirect('/upi-payment')

        # =====================================
        # CASH FLOW
        # =====================================

        else:

            save_appointment(

                session['id'],
                service,
                date,
                time,
                payment

            )

            return redirect('/success')

    # =========================================
    # GET REQUEST
    # =========================================

    service = request.args.get(
        'service',
        ''
    )

    price = float(

        request.args.get(
            'price',
            0
        )

    )

    gst = round(price * 0.18)

    total = round(price + gst)

    return render_template(

        'user/booking.html',

        username=session['user'],

        email=session['email'],

        service=service,

        price=price,

        gst=gst,

        total=total

    )


# ===================================================
# UPI PAYMENT PAGE
# ===================================================

@app.route('/upi-payment')
def upi_payment():

    if 'user' not in session:
        return redirect('/login')

    return render_template(
        'user/upi_payment.html'
    )


# ===================================================
# PAYMENT SUCCESS
# ===================================================

@app.route('/payment-success', methods=['POST'])
def payment_success():

    if 'user' not in session:
        return redirect('/login')

    upi_method = request.form['upi_method']

    booking = session.get('booking_data')

    save_appointment(

        session['id'],

        booking['service'],

        booking['date'],

        booking['time'],

        upi_method

    )

    return redirect('/success')


# ===================================================
# SUCCESS PAGE
# ===================================================

@app.route('/success')
def success():

    if 'user' not in session:
        return redirect('/login')

    return render_template(
        'user/success.html'
    )

# ===================================================
# ADMIN LOGIN
# ===================================================

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login_page():

    # =========================================
    # FORM SUBMIT
    # =========================================

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        admin = admin_login(email, password)

        if admin:

            # SAVE ADMIN SESSION
            session['admin_id'] = admin[0]
            session['admin_email'] = admin[1]

            return redirect('/admin_dashboard')

        else:

            return render_template(
                'admin/admin_login.html',
                error="Invalid Email or Password ❌"
            )

    # =========================================
    # GET REQUEST
    # =========================================

    return render_template(
        'admin/admin_login.html'
    )
# ===================================================
# ADMIN DASHBOARD
# ===================================================

@app.route('/admin_dashboard')
def admin_dashboard():

    if 'admin_id' not in session:
        return redirect('/admin_login')

    conn = sqlite3.connect('salonease.db')
    cursor = conn.cursor()

    # TOTAL USERS
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    # TOTAL SERVICES
    cursor.execute("SELECT COUNT(*) FROM services")
    total_services = cursor.fetchone()[0]

    # TOTAL BOOKINGS
    cursor.execute("SELECT COUNT(*) FROM appointments")
    total_bookings = cursor.fetchone()[0]

    # RECENT BOOKINGS
    cursor.execute("""
        SELECT * FROM appointments
        ORDER BY id DESC
        LIMIT 5
    """)

    recent_bookings = cursor.fetchall()

    conn.close()

    return render_template(
        'admin/admin_dashboard.html',
        total_users=total_users,
        total_services=total_services,
        total_bookings=total_bookings,
        recent_bookings=recent_bookings
    )
# ===================================================
# MANAGE SERVICES
# ===================================================
@app.route('/manage_services')
def manage_services():

    if 'admin_id' not in session:
        return redirect('/admin_login')

    return render_template(
        'admin/manage_services.html'
    )
# ===================================================
# MANAGE APPOINTMENTS
# ===================================================
@app.route('/manage_appointments')
def manage_appointments():

    if 'admin_id' not in session:
        return redirect('/admin_login')

    conn = sqlite3.connect('salonease.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM dappointments")
    appointments = cursor.fetchall()

    conn.close()

    return render_template(
        'admin/manage_appointments.html',
        appointments=appointments
    )
# ===================================================
# ADMIN LOGOUT
# ===================================================

@app.route('/admin_logout')
def admin_logout():

    session.pop('admin_id', None)
    session.pop('admin_email', None)

    return redirect('/admin_login')

# ===================================================
# ADD SERVICE
# ===================================================

@app.route('/add_service', methods=['GET', 'POST'])
def add_service_page():

    if 'admin_id' not in session:
        return redirect('/admin_login')

    if request.method == 'POST':

        name = request.form['name']
        price = request.form['price']
        category = request.form['category']
        image = request.form['image']

        add_service(
            name,
            price,
            category,
            image
        )

        return redirect('/manage_services')

    return render_template(
        'admin/add_service.html'
    )
# ===================================================
# DELETE SERVICE
# ===================================================

@app.route('/delete_service/<int:id>')
def remove_service(id):
    delete_service(id)
    return redirect('/manage_services')

@app.route('/confirm_appointment/<int:id>')
def confirm_appointment(id):

    conn = sqlite3.connect('salonease.db')
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE appointments SET status='Confirmed' WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect('/manage_appointments')


@app.route('/complete_appointment/<int:id>')
def complete_appointment(id):

    conn = sqlite3.connect('salonease.db')
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE appointments SET status='Completed' WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect('/manage_appointments')

# ===================================================

    if 'admin_id' not in session:
        return redirect('/admin_login')

    conn = sqlite3.connect('salonease.db')
    cursor = conn.cursor()

    # =========================
    # FILTER VALUES
    # =========================

    selected_date = request.args.get('date')
    selected_month = request.args.get('month')
    selected_week = request.args.get('week')
    selected_year = request.args.get('year')

    # =========================
    # TOTAL BOOKINGS
    # =========================

    cursor.execute("SELECT COUNT(*) FROM appointments")
    total_bookings = cursor.fetchone()[0]

    # =========================
    # CONFIRMED BOOKINGS
    # =========================

    cursor.execute("""
        SELECT COUNT(*)
        FROM appointments
        WHERE status='Confirmed'
    """)

    confirmed_bookings = cursor.fetchone()[0]

    # =========================
    # COMPLETED BOOKINGS
    # =========================

    cursor.execute("""
        SELECT COUNT(*)
        FROM appointments
        WHERE status='Completed'
    """)

    completed_bookings = cursor.fetchone()[0]

    # =========================
    # DATE WISE
    # =========================

    date_bookings = 0

    if selected_date:

        cursor.execute("""
            SELECT COUNT(*)
            FROM appointments
            WHERE date=?
        """, (selected_date,))

        date_bookings = cursor.fetchone()[0]

    # =========================
    # MONTH WISE
    # =========================

    month_bookings = 0

    if selected_month:

        cursor.execute("""
            SELECT COUNT(*)
            FROM appointments
            WHERE substr(date,1,7)=?
        """, (selected_month,))

        month_bookings = cursor.fetchone()[0]

    # =========================
    # YEAR WISE
    # =========================

    year_bookings = 0

    if selected_year:

        cursor.execute("""
            SELECT COUNT(*)
            FROM appointments
            WHERE substr(date,1,4)=?
        """, (selected_year,))

        year_bookings = cursor.fetchone()[0]

    conn.close()

    return render_template(

    'admin/reports.html',

    total_bookings=total_bookings,
    confirmed_bookings=confirmed_bookings,
    completed_bookings=completed_bookings,

    date_bookings=date_bookings,
    month_bookings=month_bookings,
    year_bookings=year_bookings,

    report_data=report_data

)
# ===================================================
# REPORTS PAGE
# ===================================================

@app.route('/reports')
def reports():

    if 'admin_id' not in session:
        return redirect('/admin_login')

    conn = sqlite3.connect('salonease.db')
    cursor = conn.cursor()

    report_data = []

    # TOTAL BOOKINGS
    cursor.execute(
        "SELECT COUNT(*) FROM appointments"
    )

    total_bookings = cursor.fetchone()[0]

    # CONFIRMED BOOKINGS
    cursor.execute(
        "SELECT COUNT(*) FROM appointments WHERE status='Confirmed'"
    )

    confirmed_bookings = cursor.fetchone()[0]

    # COMPLETED BOOKINGS
    cursor.execute(
        "SELECT COUNT(*) FROM appointments WHERE status='Completed'"
    )

    completed_bookings = cursor.fetchone()[0]

    # FILTER VALUES
    selected_date = request.args.get('date')
    selected_month = request.args.get('month')
    selected_year = request.args.get('year')

    date_bookings = 0
    month_bookings = 0
    year_bookings = 0

    # =========================
    # DATE REPORT
    # =========================

    if selected_date and selected_date != "":

        cursor.execute(
            "SELECT COUNT(*) FROM appointments WHERE date=?",
            (selected_date,)
        )

        date_bookings = cursor.fetchone()[0]

        cursor.execute(
            "SELECT * FROM appointments WHERE date=?",
            (selected_date,)
        )

        report_data = cursor.fetchall()

    # =========================
    # MONTH REPORT
    # =========================

    elif selected_month and selected_month != "":

        cursor.execute(
            "SELECT COUNT(*) FROM appointments WHERE substr(date,1,7)=?",
            (selected_month,)
        )

        month_bookings = cursor.fetchone()[0]

        cursor.execute(
            "SELECT * FROM appointments WHERE substr(date,1,7)=?",
            (selected_month,)
        )

        report_data = cursor.fetchall()

    # =========================
    # YEAR REPORT
    # =========================

    elif selected_year and selected_year != "":

        cursor.execute(
            "SELECT COUNT(*) FROM appointments WHERE substr(date,1,4)=?",
            (selected_year,)
        )

        year_bookings = cursor.fetchone()[0]

        cursor.execute(
            "SELECT * FROM appointments WHERE substr(date,1,4)=?",
            (selected_year,)
        )

        report_data = cursor.fetchall()

    conn.close()

    return render_template(

        'admin/reports.html',

        total_bookings=total_bookings,
        confirmed_bookings=confirmed_bookings,
        completed_bookings=completed_bookings,

        date_bookings=date_bookings,
        month_bookings=month_bookings,
        year_bookings=year_bookings,

        report_data=report_data

    )
@app.route('/download_report')
def download_report():

    conn = sqlite3.connect('salonease.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM appointments
    """)

    data = cursor.fetchall()

    conn.close()

    def generate():

        yield 'ID,User ID,Service,Date,Time,Payment,Status\n'

        for row in data:

            yield f'{row[0]},{row[1]},{row[2]},{row[3]},{row[4]},{row[5]},{row[6]}\n'

    return Response(

        generate(),

        mimetype='text/csv',

        headers={
            'Content-Disposition':
            'attachment;filename=SalonEase_Report.csv'
        }

    )
@app.route('/download_pdf')
def download_pdf():

    if 'admin_id' not in session:
        return redirect('/admin_login')

    conn = sqlite3.connect('salonease.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM appointments
        ORDER BY id DESC
    """)

    appointments = cursor.fetchall()

    # Statistics

    cursor.execute("""
        SELECT COUNT(*)
        FROM appointments
    """)
    total = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM appointments
        WHERE status='Confirmed'
    """)
    confirmed = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM appointments
        WHERE status='Completed'
    """)
    completed = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM appointments
        WHERE status='Pending'
    """)
    pending = cursor.fetchone()[0]

    conn.close()

    pdf_file = "SalonEase_Report.pdf"

    doc = SimpleDocTemplate(pdf_file)

    elements = []

    styles = getSampleStyleSheet()

    # ==========================
    # TITLE STYLE
    # ==========================

    title_style = styles['Title']
    title_style.alignment = TA_CENTER

    heading_style = styles['Heading2']
    heading_style.alignment = TA_CENTER

    normal_style = styles['BodyText']

    # ==========================
    # HEADER
    # ==========================

    elements.append(
        Paragraph(
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            heading_style
        )
    )

    elements.append(
        Paragraph(
            "<font color='#69B7B0'><b>SALONEASE</b></font>",
            title_style
        )
    )

    elements.append(
        Paragraph(
            "<font color='#264653'>Beauty • Style • Confidence</font>",
            heading_style
        )
    )

    elements.append(
        Paragraph(
            "Online Salon Appointment Management System",
            normal_style
        )
    )

    elements.append(
        Paragraph(
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            heading_style
        )
    )

    elements.append(Spacer(1,20))

    # ==========================
    # REPORT DETAILS
    # ==========================

    elements.append(
        Paragraph(
            "<b>REPORT TYPE:</b> Complete Appointment Report",
            normal_style
        )
    )

    elements.append(
        Paragraph(
            "<b>GENERATED BY:</b> Admin",
            normal_style
        )
    )

    elements.append(
        Paragraph(
            "<b>SYSTEM:</b> SalonEase",
            normal_style
        )
    )

    elements.append(Spacer(1,20))

    # ==========================
    # SUMMARY
    # ==========================

    elements.append(
        Paragraph(
            "<b>REPORT SUMMARY</b>",
            styles['Heading2']
        )
    )

    elements.append(
        Paragraph(
            f"""
            Total Appointments : {total}<br/>
            Confirmed Appointments : {confirmed}<br/>
            Completed Appointments : {completed}<br/>
            Pending Appointments : {pending}
            """,
            normal_style
        )
    )

    elements.append(Spacer(1,25))

    # ==========================
    # TABLE HEADING
    # ==========================

    elements.append(
        Paragraph(
            "<b>APPOINTMENT DETAILS</b>",
            styles['Heading2']
        )
    )

    elements.append(Spacer(1,10))

    # ==========================
    # TABLE DATA
    # ==========================

    data = [[
        "ID",
        "User",
        "Service",
        "Date",
        "Time",
        "Payment",
        "Status"
    ]]

    for row in appointments:

        data.append([
            row[0],
            row[1],
            row[2],
            row[3],
            row[4],
            row[5],
            row[6]
        ])

    table = Table(data)

    table.setStyle(TableStyle([

        ('BACKGROUND',(0,0),(-1,0),colors.HexColor("#69B7B0")),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),

        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),

        ('GRID',(0,0),(-1,-1),1,colors.grey),

        ('ROWBACKGROUNDS',
         (0,1),
         (-1,-1),
         [
             colors.white,
             colors.HexColor("#EEF7F5")
         ]),

        ('ALIGN',(0,0),(-1,-1),'CENTER')

    ]))

    elements.append(table)

    elements.append(Spacer(1,25))

    # ==========================
    # FOOTER
    # ==========================

    elements.append(
        Paragraph(
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            heading_style
        )
    )

    elements.append(
        Paragraph(
            "<b>Thank You For Using SalonEase</b>",
            heading_style
        )
    )

    elements.append(
        Paragraph(
            "Beauty • Style • Confidence",
            normal_style
        )
    )

    elements.append(
        Paragraph(
            "Email : support@salonease.com",
            normal_style
        )
    )

    elements.append(
        Paragraph(
            "SalonEase © 2026",
            normal_style
        )
    )

    elements.append(
        Paragraph(
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            heading_style
        )
    )

    doc.build(elements)

    return send_file(
        pdf_file,
        as_attachment=True
    )
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
    