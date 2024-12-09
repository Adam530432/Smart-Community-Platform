import matplotlib.pyplot as plt
import sqlite3
import os

# Get current script directory
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get project root directory
project_root = os.path.dirname(current_dir)
# Build database file path
db_path = os.path.join(project_root, 'data', 'community_data.db')

def analyze_and_visualize_data():
    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Read data from database
    cursor.execute('SELECT * FROM community_usage ORDER BY date')
    data = cursor.fetchall()

    # Extract data for visualization
    dates = [row[0] for row in data]
    electricity_usage = [row[1] for row in data]
    water_usage = [row[2] for row in data]
    garbage_amount = [row[3] for row in data]

    # Create multiple subplots
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 15))

    # Electricity usage chart
    ax1.plot(dates, electricity_usage, color='red')
    ax1.set_title('Daily Community Electricity Usage')
    ax1.set_ylabel('Electricity Usage (kWh)')

    # Water usage chart
    ax2.plot(dates, water_usage, color='blue')
    ax2.set_title('Daily Community Water Usage')
    ax2.set_ylabel('Water Usage (L)')

    # Garbage amount chart
    ax3.plot(dates, garbage_amount, color='green')
    ax3.set_title('Daily Community Garbage Amount')
    ax3.set_ylabel('Garbage Amount (kg)')

    # Set x-axis labels
    for ax in (ax1, ax2, ax3):
        ax.set_xlabel('Date')
        ax.tick_params(axis='x', rotation=45)

    plt.tight_layout()
    plt.show()

    # Close database connection
    conn.close()

if __name__ == "__main__":
    analyze_and_visualize_data()