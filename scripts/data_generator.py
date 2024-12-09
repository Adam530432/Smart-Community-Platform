import random
import sqlite3
import os
import names
from werkzeug.security import generate_password_hash

# Get current script directory
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get project root directory
project_root = os.path.dirname(current_dir)
# Build database file path
db_path = os.path.join(project_root, 'data', 'community_data.db')

def generate_and_store_data():
    # Ensure data directory exists
    data_dir = os.path.join(project_root, 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # Create or connect to SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

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

    # Clear existing data
    cursor.execute('DELETE FROM residents')

    # Generate 50 random resident records
    for _ in range(50):
        name = names.get_full_name()
        age = random.randint(18, 80)
        building = random.randint(1, 6)
        room = random.randint(101, 999)
        apartment_number = f'{building}-{room}'
        phone = f'1{random.randint(3, 9)}{random.randint(100000000, 999999999)}'
        password = generate_password_hash('password123')

        cursor.execute('''
        INSERT INTO residents (name, age, apartment_number, phone_number, password)
        VALUES (?, ?, ?, ?, ?)
        ''', (name, age, apartment_number, phone, password))

    conn.commit()
    conn.close()

    print(f"Data has been generated and stored in {db_path}")

if __name__ == "__main__":
    generate_and_store_data()