from utils.pg_utils import connect_pg_DB, search_novel_by_id, search_novel_by_title
import os

conn, cur = connect_pg_DB()


def get_cached_list():
    indices = []
    for entry in os.listdir("/workspace/OU_Courses/MM/cache/Gutenberg"):
        if entry.isdigit():  # Check if the folder name is all digits
            indices.append(int(entry))
    return indices


list = get_cached_list()

results = search_novel_by_id(conn, cur, list)
results = [
    {"title": row[1], "author": row[2], "genre": row[3], "id": row[4]}
    for row in results
]
print(results)
