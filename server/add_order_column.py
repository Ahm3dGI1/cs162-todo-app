"""
Migration script to add order_index column to todo_items table.
Run this script to update the database schema.
"""

import sqlite3
import os

# Get the database path
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'todos.db')

def add_order_column():
    """Add order_index column to todo_items table if it doesn't exist."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(todo_items)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'order_index' not in columns:
            print("Adding order_index column to todo_items table...")
            cursor.execute("""
                ALTER TABLE todo_items
                ADD COLUMN order_index INTEGER DEFAULT 0 NOT NULL
            """)
            conn.commit()

            # Set initial order based on created_at
            print("Setting initial order values...")
            cursor.execute("""
                UPDATE todo_items
                SET order_index = id
            """)
            conn.commit()
            print("Order column added successfully!")
        else:
            print("Order column already exists.")

    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    add_order_column()
