import sqlite3
import uuid

def init_database():

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Tables
    c.execute('''
    create table households (
        id text primary key,
        name text not null,
        location text,
        modified boolean default 1,
        created_at text default current_timestamp
        join_code text unique
        )
    ''')

    c.execute('''
    create table users (
        id text primary key,
        email text unique not null,
        first_name text not null,
        last_name text,
        household_id text not null references households(id) on delete cascade,
        created_at text default current_timestamp
        )
    ''')

    c.execute('''
    create table purchased_items (
        id text primary key,
        user_id text not null references users(id) on delete cascade,
        household_id text not null references households(id) on delete cascade,
        item_name text not null,
        quantity real not null,
        logged_at text default current_timestamp
        )
    ''')

    c.execute('''
    create table discarded_items (
        id text primary key,
        user_id text not null references users(id) on delete cascade,
        household_id text not null references households(id) on delete cascade,
        item_name text not null,
        quantity_discarded real not null,
        logged_at text default current_timestamp
        )
    ''')

    c.execute('''
    create table categories (
        id text primary key,
        name text unique not null
        )
    ''')

    c.execute('''
    create table item_categories (
        item_name text not null,
        category_id text not null references categories(id) on delete cascade,
        primary key (item_name, category_id)
        )
    ''')

    # Indexes
    c.execute('create index idx_users_household on users(household_id)')
    c.execute('create index idx_purchased_household on purchased_items(household_id)')
    c.execute('create index idx_discarded_household on discarded_items(household_id)')

    conn.commit()
    conn.close()

if __name__ == '__main__':

    init_database()
    print('Database created')
