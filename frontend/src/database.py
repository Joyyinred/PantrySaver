import sqlite3
import uuid

def log_purchased_item_local(user_id, household_id, item_name, quantity):

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute(
        'INSERT INTO purchased_items (id, user_id, household_id, item_name, quantity) VALUES (?, ?, ?, ?, ?)',
        (str(uuid.uuid4()), user_id, household_id, item_name, quantity)
    )
    c.execute('UPDATE households SET modified = 1 WHERE id = ?', (household_id,))

    conn.commit()
    conn.close()

def log_discarded_item_local(user_id, household_id, item_name, quantity_discarded):

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute(
        'INSERT INTO discarded_items (id, user_id, household_id, item_name, quantity_discarded) VALUES (?, ?, ?, ?, ?)',
        (str(uuid.uuid4()), user_id, household_id, item_name, quantity_discarded)
    )
    c.execute('UPDATE households SET modified = 1 WHERE id = ?', (household_id,))

    conn.commit()
    conn.close()
