import requests
import string
import os
import json


def preprocess_text(text):
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = " ".join(text.split())
    return text


def split_novel_into_chapters(content_list: list, body: list):
    is_chapterized = False
    for title in content_list:
        if "chapter" in title.lower():
            is_chapterized = True
            break
    splited_body = []
    content_num = 0
    current_content = []
    for line in body:
        if content_num < len(content_list) and preprocess_text(line) in preprocess_text(
            content_list[content_num]
        ):
            if content_num != 0:
                is_main_body = (
                    "chapter" in current_title.lower() if is_chapterized else True
                )
                splited_body.append(
                    {
                        "chapter_title": current_title,
                        "chapter_content": current_content,
                        "main_body": is_main_body,
                    }
                )
            current_title = content_list[content_num]
            current_content = []
            content_num += 1
        else:
            current_content.append(line)

    if content_num != 0:
        splited_body.append(
            {
                "chapter_title": current_title,
                "chapter_content": current_content,
                "main_body": is_main_body,
            }
        )
    return splited_body


def replace_special_characters(text):
    replacements = {
        "\u2014": "-",  # Em Dash
        "\u2013": "-",  # En Dash
        "\u201c": '"',  # Left Double Quotation Mark
        "\u201d": '"',  # Right Double Quotation Mark
        "\u2018": "'",  # Left Single Quotation Mark
        "\u2019": "'",  # Right Single Quotation Mark
        "\u2026": "...",  # Ellipsis
    }

    trans = str.maketrans(replacements)
    text = text.translate(trans)

    return text


def split_novel_into_pages(body_by_chapter, words_per_page):
    pages = []
    current_page = []
    current_word_count = 0

    for chapter in body_by_chapter:
        if chapter["main_body"]:
            if (
                current_page
                and current_word_count + len(chapter["chapter_title"].split())
                > words_per_page
            ):
                pages.append(current_page)
                current_page = []
                current_word_count = 0

            current_page.append("\n\n" + chapter["chapter_title"] + "\n")
            current_word_count += len(chapter["chapter_title"].split())

            for line in chapter["chapter_content"]:
                line_word_count = len(line.split())
                new_word_count = current_word_count + line_word_count
                current_page.append(line)

                if new_word_count > words_per_page:
                    pages.append(current_page)
                    current_page = []
                    current_word_count = 0
                else:
                    current_word_count = new_word_count

    if current_page:
        pages.append(current_page)

    return pages


def reformat_text(lines: list) -> list:
    merged_lines = []
    current_paragraph = ""

    for line in lines:
        if line.strip() == "":
            if current_paragraph:
                merged_lines.append(current_paragraph.strip())
                current_paragraph = ""
        else:
            current_paragraph += line.strip() + " "

    if current_paragraph:
        merged_lines.append(current_paragraph.strip())

    return merged_lines


def parse_novel_sections(lines: list):
    for end_of_info in range(len(lines)):
        if "*** START" in lines[end_of_info]:
            info_section, rest_section = lines[:end_of_info], lines[end_of_info + 1 :]
            break
    is_content_list = False
    for i in range(len(rest_section)):
        if (
            is_content_list
            and i > start
            and rest_section[i].lower().strip() in rest_section[start].lower()
        ):
            end = i
            break
        if "contents" in rest_section[i].lower():
            start = i + 2
            is_content_list = True
    content_list, body = (ele.strip() for ele in rest_section[start:end]), rest_section[
        end:
    ]
    info_section = reformat_text(info_section)
    body = reformat_text(body)
    body = [string for string in body if preprocess_text(string)]
    content_list = [ele for ele in content_list if ele]

    info_dict = {}
    for item in info_section:
        key, value = item.split(":", 1)
        info_dict[key.strip()] = value.strip()
    info_dict["content_list"] = content_list

    return info_dict, body


def remove_Gutenberg_info(lines: list) -> list:
    for start in range(len(lines)):
        if "Title:" in lines[start]:
            lines = lines[start:]
            break
    for end, item in reversed(list(enumerate(lines))):
        if "*** END OF THE PROJECT" in item:
            lines = lines[:end]
            break
    return lines


def read_novel_from_url(GutenbergID, words_per_page=500):
    print("downloading novel from gutenberg")
    url = f"https://www.gutenberg.org/cache/epub/{GutenbergID}/pg{GutenbergID}.txt.utf8"
    try:
        response = requests.get(url)
        response.encoding = "utf-8"  # Ensure correct encoding
        lines = replace_special_characters(response.text).split("\r\n")
        lines_extracted = remove_Gutenberg_info(lines)
        info, body = parse_novel_sections(lines_extracted)
        body_splited_chapters = split_novel_into_chapters(info["content_list"], body)
        body_splited_pages = split_novel_into_pages(
            body_splited_chapters, words_per_page
        )
    except requests.exceptions.ConnectionError as e:
        print("Network problem, it happens sometime.")
        return read_novel_from_url(GutenbergID)
    return info, body_splited_chapters, body_splited_pages


def save_cache_file(dir, data, filename):
    with open(os.path.join(dir, filename), "w") as file:
        json.dump(data, file, indent=4)


def get_cache_file_from_gutenberg(save_dir, GutenbergID):
    if not os.path.exists(save_dir):
        info, body_chapters, body_pages = read_novel_from_url(GutenbergID)
        os.makedirs(save_dir, exist_ok=True)
        save_cache_file(save_dir, info, "info.json")
        save_cache_file(save_dir, body_chapters, "body_chapters.json")
        save_cache_file(save_dir, body_pages, "body_pages.json")
    else:
        info = json.load(open(os.path.join(save_dir, "info.json")))
        body_chapters = json.load(open(os.path.join(save_dir, "body_chapters.json")))
        body_pages = json.load(open(os.path.join(save_dir, "body_pages.json")))
    return info, body_chapters, body_pages
