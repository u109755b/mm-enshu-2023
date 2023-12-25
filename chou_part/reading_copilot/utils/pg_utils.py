import psycopg
import numpy as np


def is_database_empty(cur):
    cur.execute(
        """
        SELECT EXISTS (
            SELECT FROM pg_tables
            WHERE schemaname = 'public'
        );
    """
    )
    return not cur.fetchone()[0]


def connect_pg_DB():
    db_params = {
        "dbname": "novelDB",
        "user": "pguser",
        "password": "1234",
        "host": "chou_pgdb",
    }

    conn = psycopg.connect(**db_params)
    cur = conn.cursor()
    return conn, cur


def set_up_novelDB(conn, cur):
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS novel (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255),
            author VARCHAR(255),
            gutenberg_id INT
        );
    """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS character (
            id SERIAL PRIMARY KEY,
            novel_id INT REFERENCES novel(id),
            character_name VARCHAR(255)
        );
    """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS node (
            id SERIAL PRIMARY KEY,
            novel_id INT REFERENCES novel(id),
            character_id INT REFERENCES character(id),
            page_index INT,
            description VARCHAR(512),
            weight INT
        );
    """
    )

    cur.execute(
        """
        ALTER TABLE character
        ADD COLUMN last_appearance_id INT REFERENCES node(id);
    """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS edge (
            id SERIAL PRIMARY KEY,
            node1 INT REFERENCES node(id),
            node2 INT REFERENCES node(id),
            page_index INT,
            description VARCHAR(512)
        );
    """
    )
    conn.commit()


def add_novel_to_DB(conn, cur, gutenbergID, info: dict):
    cur.execute("SELECT id FROM novel WHERE gutenberg_id = %s", (gutenbergID,))
    row = cur.fetchone()

    if row is not None:
        novel_id = row[0]
    else:
        cur.execute(
            """
            INSERT INTO novel (title, author, gutenberg_id)
            VALUES (%s, %s, %s) RETURNING id
        """,
            (info["Title"], info["Author"], gutenbergID),
        )

        novel_id = cur.fetchone()[0]
        conn.commit()
    return novel_id


def add_novel_to_DB_by_title(conn, cur, title, info: dict):
    cur.execute("SELECT id FROM novel WHERE title = %s", (title,))
    row = cur.fetchone()
    title = info["Title"][:255]
    author = info["Author"][:255]

    if row is not None:
        novel_id = row[0]
    else:
        cur.execute(
            """
            INSERT INTO novel (title, author, gutenberg_id)
            VALUES (%s, %s, %s) RETURNING id
        """,
            (title, author, info["GutenbergID"]),
        )

        novel_id = cur.fetchone()[0]
        conn.commit()
    return novel_id


def search_novel_by_title(conn, cur, title_vector):
    title_vector_list = (
        title_vector.tolist() if isinstance(title_vector, np.ndarray) else title_vector
    )
    cur.execute(
        """
        SELECT novel.* 
        FROM novel_title_vector
        JOIN novel ON novel_title_vector.novel_id = novel.id
        ORDER BY novel_title_vector.title_vector <-> CAST(%s AS vector) LIMIT 5;
        """,
        (title_vector_list,),
    )
    results = cur.fetchall()
    return results


def create_vector_table(conn, cur):
    cur.execute(
        """
       CREATE EXTENSION vector;
       """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS novel_title_vector (
            id bigserial PRIMARY KEY,
            novel_id integer REFERENCES novel(id),
            title_vector vector(384)
        );
    """
    )
    conn.commit()

    print("Table 'novel_title_vector' created successfully")


def add_tile_to_vector_talbe(conn, cur, novel_id, title_vector):
    title_vector_list = (
        title_vector.tolist() if isinstance(title_vector, np.ndarray) else title_vector
    )
    cur.execute(
        "INSERT INTO novel_title_vector (novel_id, title_vector) VALUES (%s, %s);",
        (novel_id, title_vector_list),
    )
    conn.commit()
    print(f"\r{novel_id} added to the vector table.", end="")
