import requests
import json
import os
from utils.pg_utils import connect_pg_DB, add_novel_to_DB_by_title

book_info = []
url = "https://gutendex.com/books/?languages=en"
save_dir = os.path.join(os.getcwd(), "cache/Gutenberg")

while url != None:
    page = requests.get(url)
    page_text = page.content.decode("utf-8")
    page_data = json.loads(page_text)
    for book in page_data["results"]:
        if book["media_type"] != "Text":
            continue
        is_english = False
        for language in book["languages"]:
            if language == "en":
                is_english = True
                break
        is_fiction = False
        for subject in book["subjects"]:
            if " fiction" in subject.lower():
                is_fiction = True
                break
        if is_fiction and is_english:
            authors = []
            for author in book["authors"]:
                authors.append(author["name"])
            book_info.append(
                {
                    "Title": book["title"],
                    "Author": (", ".join(authors)),
                    "GutenbergID": book["id"],
                    "Language": (", ".join(book["languages"])),
                }
            )
    with open(os.path.join(save_dir, "book_info.json"), "w") as file:
        json.dump(book_info, file, indent=4)
    url = page_data["next"]


read_dir = os.path.join(os.getcwd(), "cache/Gutenberg")
conn, cur = connect_pg_DB()


with open(os.path.join(read_dir, "book_info.json"), "r") as file:
    book_info = json.load(file)
    total = len(book_info)
    for i, book in enumerate(book_info):
        novel_id = add_novel_to_DB_by_title(conn, cur, book["Title"], book)
        print(f"\r{book['Title']} added, {i+1}/{total}", end="")

cur.close()
conn.close()
