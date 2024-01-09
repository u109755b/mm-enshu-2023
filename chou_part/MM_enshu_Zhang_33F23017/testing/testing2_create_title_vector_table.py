from utils.pg_utils import connect_pg_DB, add_title_to_vector_talbe, create_vector_table
from sentence_transformers import SentenceTransformer

# This script is used to create the title vector table using pgvector extension and sentence-transformers.

conn, cur = connect_pg_DB()
model = SentenceTransformer("sentence-transformers/all-MiniLM-L12-v2")

# create_vector_table(conn, cur)  # Only need to run once

cur.execute("SELECT id, title FROM novel;")
novels = cur.fetchall()

for novel_id, title in novels:
    embedding = model.encode(title)
    add_title_to_vector_talbe(conn, cur, novel_id, embedding)

cur.close()
conn.close()
