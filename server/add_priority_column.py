"""
Migration script to add priority column to todo_items table.
Run this script to update the database schema.
"""

import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'instance', 'todos.db')

def add_priority_column():
    """Add priority column to todo_items table if it doesn't exist."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("PRAGMA table_info(todo_items)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'priority' not in columns:
            print("Adding priority column to todo_items table...")
            cursor.execute("""
                ALTER TABLE todo_items
                ADD COLUMN priority VARCHAR(10) DEFAULT 'medium' NOT NULL
            """)
            conn.commit()
            print("Priority column added successfully!")
        else:
            print("Priority column already exists.")

    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    add_priority_column()
