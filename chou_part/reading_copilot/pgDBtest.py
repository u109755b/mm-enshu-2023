import psycopg

# Database connection parameters - replace these with your details
db_params = {
    "dbname": "novelDB",
    "user": "pguser",
    "password": "1234",
    "host": "chou_pgdb",  # or your database server address
}

# SQL command to create a table
create_table_command = """
CREATE TABLE testTB (
    id serial PRIMARY KEY,
    name varchar(100),
    description text
);
"""

# Connect to your database
conn = None
cur = None
try:
    print("Connecting to the PostgreSQL database...")
    conn = psycopg.connect(**db_params)
    cur = conn.cursor()

    # Execute the SQL command
    cur.execute(create_table_command)
    print("Table 'testTB' created successfully")

    # Commit the changes to the database
    conn.commit()

except Exception as e:
    print(f"An error occurred: {e}")
    if conn:
        conn.rollback()

finally:
    # Close the cursor and connection
    if cur:
        cur.close()
    if conn:
        conn.close()
