import sqlite3

def log_purchased_item_local(user_id, household_id, item_name, quantity):

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute(
        'insert into purchased_items (household_id, item_name, quantity) values (?, ?, ?)',
        (household_id, item_name, quantity)
    )
    c.execute('update households set modified = 1 where id = ?', (household_id,))

    conn.commit()
    conn.close()

def log_discarded_item_local(user_id, household_id, item_name, quantity_discarded):

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute(
        'insert into discarded_items (household_id, item_name, quantity_discarded) values (?, ?, ?)',
        (household_id, item_name, quantity_discarded)
    )
    c.execute('update households set modified = 1 where id = ?', (household_id,))

    conn.commit()
    conn.close()
