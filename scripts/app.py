import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, Response, g
import sqlite3
import random
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash, generate_password_hash
import csv
from io import StringIO

# Get current script directory
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get project root directory
project_root = os.path.dirname(current_dir)


app = Flask(__name__,
            template_folder=os.path.join(project_root, 'templates'),
            static_folder=os.path.join(project_root, 'static'))

app.secret_key = 'your_secret_key'  # For session and flash messages

# Build database file path
DATABASE = os.path.join(project_root, 'instance', 'community.db')

# Database connection function

# Modify database connection function
def get_db():
    if 'db' not in g:
        # Ensure instance directory exist
        os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        conn = get_db()
        cursor = conn.cursor()

        # Create visitor records table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS visitor_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            visitor_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            visit_apartment TEXT NOT NULL,
            purpose TEXT NOT NULL,
            visit_time DATETIME NOT NULL,
            status TEXT NOT NULL DEFAULT 'Visiting'
        )
        ''')

        # Create residents table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS residents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            apartment_number TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            password TEXT NOT NULL
        )
        ''')

        # Create admins table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
        ''')

        # Create maintenance records table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS maintenance_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            description TEXT NOT NULL,
            location TEXT NOT NULL,
            contact TEXT NOT NULL,
            submit_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'Pending'
        )
        ''')

        # Create utility bills table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS utility_bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            apartment_number TEXT NOT NULL,
            bill_type TEXT NOT NULL,
            amount REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'Unpaid',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Create notices table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS notices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Create activities table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            date DATE NOT NULL,
            location TEXT NOT NULL,
            status TEXT DEFAULT 'Not Started'
        )
        ''')

        # Check if residents table is empty
        cursor.execute('SELECT COUNT(*) FROM residents')
        if cursor.fetchone()[0] == 0:
            # Add default admin account
            cursor.execute('''
            INSERT INTO admins (username, password)
            VALUES (?, ?)
            ''', ('admin', generate_password_hash('admin123')))

        conn.commit()
        print("Database initialized successfully.")


def generate_mock_weather():
    weather_conditions = ['Sunny', 'Cloudy', 'Overcast', 'Light Rain', 'Heavy Rain', 'Thunderstorm']
    weather_icons = ['01d', '02d', '03d', '10d', '09d', '11d']

    mock_weather = []
    for i in range(5):  # Generate weather data for next 5 days
        date = datetime.now() + timedelta(days=i)
        condition_index = random.randint(0, len(weather_conditions) - 1)
        condition = weather_conditions[condition_index]
        icon = weather_icons[condition_index]
        temp = random.randint(23, 35)  # Temperature range for tropical climate

        mock_weather.append({
            'dt_txt': date.strftime('%Y-%m-%d 12:00:00'),
            'main': {'temp': temp},
            'weather': [{'description': condition, 'icon': icon}]
        })

    return mock_weather


def get_weather_icon(icon_code):
    icon_map = {
        '01d': 'sun',
        '01n': 'moon',
        '02d': 'cloud-sun',
        '02n': 'cloud-moon',
        '03d': 'cloud',
        '03n': 'cloud',
        '04d': 'cloud',
        '04n': 'cloud',
        '09d': 'cloud-showers-heavy',
        '09n': 'cloud-showers-heavy',
        '10d': 'cloud-sun-rain',
        '10n': 'cloud-moon-rain',
        '11d': 'bolt',
        '11n': 'bolt',
        '13d': 'snowflake',
        '13n': 'snowflake',
        '50d': 'smog',
        '50n': 'smog'
    }
    return icon_map.get(icon_code, 'question')


# Route definitions
@app.route('/')
def index():
    unpaid_bills_count = 0
    if 'user_id' in session:
        conn = get_db()
        user = conn.execute('SELECT * FROM residents WHERE id = ?', (session['user_id'],)).fetchone()
        unpaid_bills_count = conn.execute(
            'SELECT COUNT(*) FROM utility_bills WHERE apartment_number = ? AND status = "Unpaid"',
            (user['apartment_number'],)
        ).fetchone()[0]

    weather_data = generate_mock_weather()
    return render_template('index.html',
                           unpaid_bills_count=unpaid_bills_count,
                           weather_data=weather_data,
                           get_weather_icon=get_weather_icon)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # If user is already logged in, redirect to dashboard
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Print debug information
        print(f"Login attempt - Username: {username}")

        error = None
        conn = get_db()

        if not username:
            error = 'Please enter username or phone number'
        elif not password:
            error = 'Please enter password'
        else:
            # Try to find user by username or phone number
            user = conn.execute(
                'SELECT * FROM residents WHERE name = ? OR phone_number = ?',
                (username, username)
            ).fetchone()

            print(f"Found user: {user is not None}")  # Debug information

            if user is None:
                error = 'Username or phone number does not exist'
            elif not check_password_hash(user['password'], password):
                error = 'Incorrect password'
            else:
                # Login successful
                session.clear()
                session['user_id'] = user['id']
                print(f"Login successful for user ID: {user['id']}")  # Debug information
                return redirect(url_for('dashboard'))

        if error:
            flash(error, 'error')
            print(f"Login error: {error}")  # Debug information

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have successfully logged out', 'success')
    return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    user = conn.execute('SELECT * FROM residents WHERE id = ?', (session['user_id'],)).fetchone()
    bills = conn.execute(
        'SELECT * FROM utility_bills WHERE apartment_number = ? AND status = "Unpaid"',
        (user['apartment_number'],)
    ).fetchall()

    maintenance_records = conn.execute(
        'SELECT * FROM maintenance_records WHERE contact = ? ORDER BY submit_time DESC',
        (user['phone_number'],)
    ).fetchall()

    return render_template('dashboard.html',
                           user=user,
                           bills=bills,
                           maintenance_records=maintenance_records)


@app.route('/api/dashboard/stats')
def get_dashboard_stats():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    conn = get_db()
    stats = {
        'total_residents': conn.execute('SELECT COUNT(*) FROM residents').fetchone()[0],
        'total_households': conn.execute('SELECT COUNT(DISTINCT apartment_number) FROM residents').fetchone()[0],
        'total_buildings': 8,  # Fixed value
        'monthly_fees': 56789  # Example value
    }

    # Retrieve age distribution data
    age_distribution = conn.execute('''
        SELECT 
            CASE 
                WHEN age < 18 THEN '0-17'
                WHEN age BETWEEN 18 AND 30 THEN '18-30'
                WHEN age BETWEEN 31 AND 50 THEN '31-50'
                WHEN age BETWEEN 51 AND 70 THEN '51-70'
                ELSE '70+'
            END as age_group,
            COUNT(*) as count
        FROM residents
        GROUP BY age_group
        ORDER BY age_group
    ''').fetchall()

    # Retrieve maintenance statistics
    maintenance_stats = conn.execute('''
        SELECT type, COUNT(*) as count
        FROM maintenance_records
        GROUP BY type
    ''').fetchall()

    # Retrieve billing statistics
    billing_stats = conn.execute('''
        SELECT bill_type, COUNT(*) as count, SUM(amount) as total
        FROM utility_bills
        GROUP BY bill_type
    ''').fetchall()

    return jsonify({
        'stats': stats,
        'age_distribution': [dict(row) for row in age_distribution],
        'maintenance_stats': [dict(row) for row in maintenance_stats],
        'billing_stats': [dict(row) for row in billing_stats]
    })

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    # If admin is already logged in, redirect to admin dashboard
    if 'admin_id' in session:
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        error = None

        if not username:
            error = 'Username is required'
        elif not password:
            error = 'Password is required'
        else:
            conn = get_db()
            admin = conn.execute(
                'SELECT * FROM admins WHERE username = ?', (username,)
            ).fetchone()

            if admin is None:
                error = 'Invalid username'
            elif not check_password_hash(admin['password'], password):
                error = 'Invalid password'
            else:
                # Login successful
                session.clear()
                session['admin_id'] = admin['id']
                return redirect(url_for('admin_dashboard'))

        if error:
            flash(error, 'error')

    return render_template('admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    # Clear admin session
    session.pop('admin_id', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('admin_login'))


@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    conn = get_db()
    try:
        # Get all residents data
        residents = conn.execute('''
            SELECT * FROM residents 
            ORDER BY name
        ''').fetchall()

        # Get maintenance records
        maintenance_records = conn.execute('''
            SELECT * FROM maintenance_records 
            ORDER BY submit_time DESC
        ''').fetchall()

        # Get visitor records
        visitor_records = conn.execute('''
            SELECT * FROM visitor_records 
            ORDER BY visit_time DESC
        ''').fetchall()

        # Get utility bills
        utility_bills = conn.execute('''
            SELECT * FROM utility_bills 
            ORDER BY created_at DESC
        ''').fetchall()

        return render_template('admin_dashboard.html',
                             residents=residents,
                             maintenance_records=maintenance_records,
                             visitor_records=visitor_records,
                             utility_bills=utility_bills)
    except Exception as e:
        print(f"Error in admin_dashboard: {str(e)}")
        flash('An error occurred while loading the dashboard', 'error')
        return redirect(url_for('admin_login'))


@app.route('/admin/export_residents')
def export_residents():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    conn = get_db()
    residents = conn.execute('SELECT * FROM residents').fetchall()

    # Create CSV string
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'Name', 'Age', 'Apartment', 'Phone'])  # Headers
    
    # Write data
    for resident in residents:
        cw.writerow([resident['id'], resident['name'], resident['age'],
                    resident['apartment_number'], resident['phone_number']])

    output = si.getvalue()
    si.close()

    return Response(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=residents.csv'}
    )

@app.route('/residents')
def residents():
    conn = get_db()
    try:
        print("Fetching residents data...")

        all_residents = conn.execute('''
            SELECT * FROM residents 
            ORDER BY name
        ''').fetchall()

        # Format data for DataTables
        data = []
        for resident in all_residents:
            data.append({
                'id': resident['id'],
                'name': resident['name'],
                'age': resident['age'],
                'apartment_number': resident['apartment_number'],
                'phone_number': resident['phone_number']
            })

        return jsonify({'data': data})

    except Exception as e:
        print(f"Error fetching residents: {str(e)}")
        return jsonify({'error': 'Failed to fetch residents data'}), 500


@app.route('/admin/add_resident', methods=['POST'])
def add_resident():
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    # Get form data
    name = request.form.get('name')
    age = request.form.get('age')
    apartment = request.form.get('apartment')
    phone = request.form.get('phone')
    password = request.form.get('password')

    # Validate input
    if not all([name, age, apartment, phone, password]):
        return jsonify({'error': 'All fields are required'}), 400

    try:
        age = int(age)
    except ValueError:
        return jsonify({'error': 'Age must be a number'}), 400

    conn = get_db()
    try:
        # Check if phone numbers already exists
        existing_user = conn.execute(
            'SELECT * FROM residents WHERE phone_number = ?',
            (phone,)
        ).fetchone()

        if existing_user:
            return jsonify({'error': 'Phone number already registered'}), 400

        # Insert new resident
        cursor = conn.execute('''
            INSERT INTO residents (name, age, apartment_number, phone_number, password)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, age, apartment, phone, generate_password_hash(password)))

        conn.commit()

        # Get the newly created resident
        new_resident = conn.execute(
            'SELECT * FROM residents WHERE id = ?',
            (cursor.lastrowid,)
        ).fetchone()

        return jsonify({
            'message': 'Resident added successfully',
            'resident': {
                'id': new_resident['id'],
                'name': new_resident['name'],
                'age': new_resident['age'],
                'apartment_number': new_resident['apartment_number'],
                'phone_number': new_resident['phone_number']
            }
        })

    except Exception as e:
        print(f"Error adding resident: {str(e)}")
        return jsonify({'error': 'Failed to add resident'}), 500


@app.route('/admin/edit_resident/<int:resident_id>', methods=['POST'])
def edit_resident(resident_id):
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    # Get form data
    name = request.form.get('name')
    age = request.form.get('age')
    apartment = request.form.get('apartment')
    phone = request.form.get('phone')
    password = request.form.get('password')

    # Validate input
    if not all([name, age, apartment, phone]):
        return jsonify({'error': 'Name, age, apartment, and phone are required'}), 400

    try:
        age = int(age)
    except ValueError:
        return jsonify({'error': 'Age must be a number'}), 400

    conn = get_db()
    try:
        # Check if phone number already exists for other residents
        existing_user = conn.execute(
            'SELECT * FROM residents WHERE phone_number = ? AND id != ?',
            (phone, resident_id)
        ).fetchone()

        if existing_user:
            return jsonify({'error': 'Phone number already registered to another resident'}), 400

        # Update resident information
        if password:  # If password is provided, update it too
            conn.execute('''
                UPDATE residents 
                SET name = ?, age = ?, apartment_number = ?, 
                    phone_number = ?, password = ?
                WHERE id = ?
            ''', (name, age, apartment, phone, 
                 generate_password_hash(password), resident_id))
        else:  # If no password provided, update other fields only
            conn.execute('''
                UPDATE residents 
                SET name = ?, age = ?, apartment_number = ?, 
                    phone_number = ?
                WHERE id = ?
            ''', (name, age, apartment, phone, resident_id))

        conn.commit()

        # Get updated resident data
        updated_resident = conn.execute(
            'SELECT * FROM residents WHERE id = ?',
            (resident_id,)
        ).fetchone()

        return jsonify({
            'message': 'Resident updated successfully',
            'resident': {
                'id': updated_resident['id'],
                'name': updated_resident['name'],
                'age': updated_resident['age'],
                'apartment_number': updated_resident['apartment_number'],
                'phone_number': updated_resident['phone_number']
            }
        })

    except Exception as e:
        print(f"Error updating resident: {str(e)}")
        return jsonify({'error': 'Failed to update resident'}), 500
    
    @app.route('/admin/delete_resident/<int:resident_id>', methods=['POST'])
def delete_resident(resident_id):
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    conn = get_db()
    try:
        # Check if resident exists
        resident = conn.execute(
            'SELECT * FROM residents WHERE id = ?',
            (resident_id,)
        ).fetchone()

        if not resident:
            return jsonify({'error': 'Resident not found'}), 404

        # Delete the resident
        conn.execute('DELETE FROM residents WHERE id = ?', (resident_id,))
        conn.commit()

        return jsonify({'message': 'Resident deleted successfully'})

    except Exception as e:
        print(f"Error deleting resident: {str(e)}")
        return jsonify({'error': 'Failed to delete resident'}), 500


@app.route('/admin/maintenance')
def admin_maintenance():
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    conn = get_db()
    try:
        # Get all maintenance records
        maintenance_records = conn.execute('''
            SELECT * FROM maintenance_records 
            ORDER BY submit_time DESC
        ''').fetchall()

        # Format data for response
        data = []
        for record in maintenance_records:
            data.append({
                'id': record['id'],
                'type': record['type'],
                'description': record['description'],
                'location': record['location'],
                'contact': record['contact'],
                'submit_time': record['submit_time'],
                'status': record['status']
            })

        return jsonify({'data': data})

    except Exception as e:
        print(f"Error fetching maintenance records: {str(e)}")
        return jsonify({'error': 'Failed to fetch maintenance records'}), 500


@app.route('/admin/update_maintenance/<int:record_id>', methods=['POST'])
def update_maintenance(record_id):
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    # Get new status from form
    new_status = request.form.get('status')
    if not new_status:
        return jsonify({'error': 'Status is required'}), 400

    conn = get_db()
    try:
        # Update maintenance record status
        conn.execute('''
            UPDATE maintenance_records 
            SET status = ? 
            WHERE id = ?
        ''', (new_status, record_id))
        conn.commit()

        # Get updated record
        updated_record = conn.execute(
            'SELECT * FROM maintenance_records WHERE id = ?',
            (record_id,)
        ).fetchone()

        return jsonify({
            'message': 'Maintenance record updated successfully',
            'record': {
                'id': updated_record['id'],
                'type': updated_record['type'],
                'description': updated_record['description'],
                'location': updated_record['location'],
                'contact': updated_record['contact'],
                'submit_time': updated_record['submit_time'],
                'status': updated_record['status']
            }
        })

    except Exception as e:
        print(f"Error updating maintenance record: {str(e)}")
        return jsonify({'error': 'Failed to update maintenance record'}), 500


@app.route('/admin/visitors')
def admin_visitors():
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    conn = get_db()
    try:
        # Get all visitor records
        visitor_records = conn.execute('''
            SELECT * FROM visitor_records 
            ORDER BY visit_time DESC
        ''').fetchall()

        # Format data for response
        data = []
        for record in visitor_records:
            data.append({
                'id': record['id'],
                'visitor_name': record['visitor_name'],
                'phone': record['phone'],
                'visit_apartment': record['visit_apartment'],
                'purpose': record['purpose'],
                'visit_time': record['visit_time'],
                'status': record['status']
            })

        return jsonify({'data': data})

    except Exception as e:
        print(f"Error fetching visitor records: {str(e)}")
        return jsonify({'error': 'Failed to fetch visitor records'}), 500
    
    @app.route('/admin/update_visitor/<int:record_id>', methods=['POST'])
def update_visitor(record_id):
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    # Get new status from form
    new_status = request.form.get('status')
    if not new_status:
        return jsonify({'error': 'Status is required'}), 400

    conn = get_db()
    try:
        # Update visitor record status
        conn.execute('''
            UPDATE visitor_records 
            SET status = ? 
            WHERE id = ?
        ''', (new_status, record_id))
        conn.commit()

        # Get updated record
        updated_record = conn.execute(
            'SELECT * FROM visitor_records WHERE id = ?',
            (record_id,)
        ).fetchone()

        return jsonify({
            'message': 'Visitor record updated successfully',
            'record': {
                'id': updated_record['id'],
                'visitor_name': updated_record['visitor_name'],
                'phone': updated_record['phone'],
                'visit_apartment': updated_record['visit_apartment'],
                'purpose': updated_record['purpose'],
                'visit_time': updated_record['visit_time'],
                'status': updated_record['status']
            }
        })

    except Exception as e:
        print(f"Error updating visitor record: {str(e)}")
        return jsonify({'error': 'Failed to update visitor record'}), 500


@app.route('/admin/bills')
def admin_bills():
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    conn = get_db()
    try:
        # Get all utility bills
        utility_bills = conn.execute('''
            SELECT * FROM utility_bills 
            ORDER BY created_at DESC
        ''').fetchall()

        # Format data for response
        data = []
        for bill in utility_bills:
            data.append({
                'id': bill['id'],
                'apartment_number': bill['apartment_number'],
                'bill_type': bill['bill_type'],
                'amount': bill['amount'],
                'status': bill['status'],
                'created_at': bill['created_at']
            })

        return jsonify({'data': data})

    except Exception as e:
        print(f"Error fetching utility bills: {str(e)}")
        return jsonify({'error': 'Failed to fetch utility bills'}), 500


@app.route('/admin/update_bill/<int:bill_id>', methods=['POST'])
def update_bill(bill_id):
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    # Get new status from form
    new_status = request.form.get('status')
    if not new_status:
        return jsonify({'error': 'Status is required'}), 400

    conn = get_db()
    try:
        # Update bill status
        conn.execute('''
            UPDATE utility_bills 
            SET status = ? 
            WHERE id = ?
        ''', (new_status, bill_id))
        conn.commit()

        # Get updated bill
        updated_bill = conn.execute(
            'SELECT * FROM utility_bills WHERE id = ?',
            (bill_id,)
        ).fetchone()

        return jsonify({
            'message': 'Bill updated successfully',
            'bill': {
                'id': updated_bill['id'],
                'apartment_number': updated_bill['apartment_number'],
                'bill_type': updated_bill['bill_type'],
                'amount': updated_bill['amount'],
                'status': updated_bill['status'],
                'created_at': updated_bill['created_at']
            }
        })

    except Exception as e:
        print(f"Error updating bill: {str(e)}")
        return jsonify({'error': 'Failed to update bill'}), 500