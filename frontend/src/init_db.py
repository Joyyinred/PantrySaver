import sqlite3

def init_database():

    conn = sqlite3.connect('database.db')
    conn.execute('pragma foreign_keys = on;')
    c = conn.cursor()

    c.execute('''
    create table if not exists households (
        id text primary key default (lower(hex(randomblob(16)))),
        name text not null,
        location text,
        created_at text default current_timestamp,
        modified boolean default 1,
        join_code text unique,
        global_aggression real default 1.0
        )
    ''')

    c.execute('''
    create table if not exists users (
        id text primary key default (lower(hex(randomblob(16)))),
        email text unique not null,
        household_id text not null references households(id) on delete cascade,
        created_at text default current_timestamp,
        first_name text not null,
        last_name text
        )
    ''')

    c.execute('''
    create table if not exists admins (
        id text primary key default (lower(hex(randomblob(16)))),
        user_id text unique,
        email text unique not null,
        display_name text,
        is_active boolean default 1,
        created_at text default current_timestamp
        )
    ''')

    c.execute('''
    create table if not exists purchased_items (
        id text primary key default (lower(hex(randomblob(16)))),
        household_id text not null references households(id) on delete cascade,
        item_name text not null,
        quantity real not null,
        logged_at text default current_timestamp,
        category text
        )
    ''')

    c.execute('''
    create table if not exists item_intelligence (
        household_id text not null references households(id) on delete cascade,
        item_name text not null,
        item_weight real default 1.0,
        primary key (household_id, item_name)
        )
    ''')

    c.execute('''
    create table if not exists discarded_items (
        id text primary key default (lower(hex(randomblob(16)))),
        household_id text not null references households(id) on delete cascade,
        item_name text not null,
        quantity_discarded real not null,
        logged_at text default current_timestamp,
        category text
        )
    ''')

    c.execute('''
    create table if not exists categories (
        id text primary key default (lower(hex(randomblob(16)))),
        name text unique not null
        )
    ''')

    c.execute('''
    create table if not exists item_categories (
        item_name text not null,
        category_id text not null references categories(id) on delete cascade,
        primary key (item_name, category_id)
        )
    ''')

    c.execute('''
    create table if not exists ratios (
        id integer primary key autoincrement,
        household_id text references households(id) on delete cascade,
        item_name text,
        ratio real,
        portion real
        )
    ''')

    c.execute('''
    create table if not exists recommendation_templates (
        id integer primary key autoincrement,
        type text not null, -- 'ask', 'alert', or 'tip'
        template_text text not null unique
        )
    ''')

    templates = [
        ('ask', 'Did you recently buy !ITEM! and forgot to log it?'),
        ('ask', 'Is !ITEM! still in your inventory?'),
        ('alert', 'There is a high risk that your !ITEM! will go bad soon. Use or donate it!'),
        ('alert', 'Your !ITEM! is reaching its limit. Please process it today.'),
        ('tip', 'Why not use your !ITEM! in a fresh salad today?'),
        ('tip', 'Boost your nutrition by adding !ITEM! to your next meal!')
    ]
    c.execute('select count(*) from recommendation_templates')

    if c.fetchone()[0] == 0:
        c.executemany('insert into recommendation_templates (type, template_text) values (?, ?)', templates)

    c.execute('''
    create table if not exists recommendations (
        id text primary key default (lower(hex(randomblob(16)))),
        household_id text not null references households(id) on delete cascade,
        template_id integer,
        item_name text not null,
        type text not null,
        subtitle text not null,
        score real default 0.0,
        feedback integer default null,
        is_active boolean default 1,
        created_at text default current_timestamp,
        responded_at text
        )
    ''')

    # indexes for query performance
    c.execute('create index if not exists idx_users_household on users(household_id)')
    c.execute('create index if not exists idx_purchased_household on purchased_items(household_id)')
    c.execute('create index if not exists idx_discarded_household on discarded_items(household_id)')
    c.execute('create index if not exists idx_ratios_household on ratios(household_id)')
    c.execute('create index if not exists idx_admins_user on admins(user_id)')

    conn.commit()
    conn.close()

if __name__ == '__main__':

    init_database()
    print('database created successfully')
