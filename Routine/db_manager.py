import sqlite3

DB_NAME = "routine_manager_v3.db"  # Database filename

def connect_db():
    """Create a database connection."""
    return sqlite3.connect(DB_NAME)

def init_db(drop_tables=False):
    """Initialize the database with required tables."""
    conn = connect_db()
    cur = conn.cursor()
    
    if drop_tables:
        cur.execute("DROP TABLE IF EXISTS routines")
        cur.execute("DROP TABLE IF EXISTS logs")
        cur.execute("DROP TABLE IF EXISTS properties")
    
    # Table creation SQL
    cur.execute("""
        CREATE TABLE IF NOT EXISTS routines (
            id INTEGER PRIMARY KEY,
            order_num INTEGER,
            name TEXT UNIQUE,
            duration INTEGER,
            path TEXT,
            created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            due_date DATETIME DEFAULT NULL,
            short_description TEXT DEFAULT NULL,
            description TEXT DEFAULT NULL,
            human_name TEXT DEFAULT NULL,
            verified INTEGER DEFAULT 0,
            importance TEXT DEFAULT 'not',
            status TEXT DEFAULT 'not stated',
            price REAL DEFAULT 0,
            repeat TEXT DEFAULT 'none',
            days TEXT DEFAULT '0,0,0,0,0,0,0',
            contact TEXT DEFAULT '',
            email TEXT DEFAULT '',
            link TEXT DEFAULT 'https://',
            other_properties TEXT DEFAULT ''
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY,
            routine_name TEXT,
            start_time TEXT,
            end_time TEXT,
            status TEXT
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS properties (
            property_id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            name TEXT,
            path TEXT
        )
    """)
    conn.commit()
    conn.close()

def fetch_routine_data(routine_name):
    """Fetch routine data from the SQLite database."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM routines WHERE name = ?", (routine_name,))
    data = cur.fetchone()
    conn.close()
    return data

# Additional database operations can be added here.

def fetch_routine_names():
    """Fetch all routine names from the SQLite database."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT name FROM routines")
    data = cur.fetchall()
    conn.close()
    return [name[0] for name in data]

def fetch_all_routines():
    """Fetch all routines from the SQLite database."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM routines")
    data = cur.fetchall()
    conn.close()
    return data

def fetch_logs(routine_name):
    """Fetch logs for a specific routine from the SQLite database."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM logs WHERE routine_name = ?", (routine_name,))
    data = cur.fetchall()
    conn.close()
    return data

def insert_routine(data):
    """Insert a new routine into the SQLite database."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO routines (
            order_num, name, duration, path, due_date, short_description, description,
            human_name, verified, importance, status, price, repeat, days, contact, email, link, other_properties
        ) VALUES (?,    ?,    ?,        ?,    ?,        ?,               ?,           ?,          ?,       ?,         ?,     ?,     ?,     ?,    ?,      ?,     ?,    ?)
    """, data)  
    conn.commit()
    conn.close()
    
def update_routine(data):
    """Update an existing routine in the SQLite database."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE routines SET
            order_num = ?, duration = ?, path = ?, due_date = ?, short_description = ?, description = ?,
            human_name = ?, verified = ?, importance = ?, status = ?, price = ?, repeat = ?, days = ?,
            contact = ?, email = ?, link = ?, other_properties = ?
        WHERE name = ?
    """, data[1:] + (data[0],))
    conn.commit()
    conn.close()    
    
def delete_routine(routine_name):
    """Delete a routine from the SQLite database."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM routines WHERE name = ?", (routine_name,))
    conn.commit()
    conn.close()
    
def insert_log(data):
    """Insert a new log entry into the SQLite database."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO logs (routine_name, start_time, end_time, status) VALUES (?, ?, ?, ?)", data)
    conn.commit()
    conn.close()
    
def insert_property(data):
    """Insert a new property into the SQLite database."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO properties (type, name, path) VALUES (?, ?, ?)", data)
    conn.commit()
    conn.close()

def fetch_properties():
    """Fetch all properties from the SQLite database."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM properties")
    data = cur.fetchall()
    conn.close()
    return data

def delete_property(property_id):
    """Delete a property from the SQLite database."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM properties WHERE property_id = ?", (property_id,))
    conn.commit()
    conn.close()

def update_property(data):
    """Update an existing property in the SQLite database."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("UPDATE properties SET type = ?, name = ?, path = ? WHERE property_id = ?", data)
    conn.commit()
    conn.close()
        