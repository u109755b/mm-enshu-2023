from utils.pg_utils import connect_pg_DB, search_novel_by_title
from sentence_transformers import SentenceTransformer

conn, cur = connect_pg_DB()
model = SentenceTransformer("sentence-transformers/all-MiniLM-L12-v2")

while True:
    user_input = input("Enter a novel title to search (type 'END' to exit): ")

    if user_input.strip().upper() == "END":
        print("Exiting the program.")
        break

    user_input_vector = model.encode(user_input)

    results = search_novel_by_title(conn, cur, user_input_vector)

    if results:
        print("Top matching novels:")
        for row in results:
            print(row)
    else:
        print("No matches found.")
    print("\n" + "-" * 50 + "\n")

cur.close()
conn.close()
