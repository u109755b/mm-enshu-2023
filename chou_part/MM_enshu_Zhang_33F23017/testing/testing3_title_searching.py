from utils.pg_utils import connect_pg_DB, search_novel_by_title
from sentence_transformers import SentenceTransformer
import argparse

# This is the prototype program used to search novels gutenberg id by title using pgvector extension and sentence-transformers.

parser = argparse.ArgumentParser()
parser.add_argument(
    "--top_k",
    type=int,
    help="The number of most likely results to be shown.",
    default=5,
)
args = parser.parse_args()


def main():
    conn, cur = connect_pg_DB()
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L12-v2")

    while True:
        user_input = input("Enter a novel title to search (type 'END' to exit): ")

        if user_input.strip().upper() == "END":
            print("Exiting the program.")
            break

        user_input_vector = model.encode(user_input)

        results = search_novel_by_title(conn, cur, user_input_vector, top_k=args.top_k)

        if results:
            print("Top matching novels:")
            for row in results:
                print(row)
        else:
            print("No matches found.")
        print("\n" + "-" * 50 + "\n")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
