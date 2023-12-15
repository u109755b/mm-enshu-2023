import requests
import re
import mwclient
import json

def get_wikipedia_page_info(title):
    base_url = "https://en.wikipedia.org/w/api.php"
    params = {
        'action': 'query',
        'format': 'json',
        'titles': title,
        'prop': 'revisions',
        'rvprop': 'content'
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    # ページが存在するか確認
    page_id = list(data['query']['pages'].keys())[0]
    if page_id == '-1':
        print(f"ページ '{title}' は存在しません。")
        return None

    # ページの情報を抽出
    page_info = data['query']['pages'][page_id]['revisions'][0]['*']
    return page_info

def get_wikipedia_section(page_title, section_title):
    site = mwclient.Site("en.wikipedia.org")
    try:
        page = site.pages[page_title]
        content = page.text()
        # 正規表現パターンを調整してセクションとそのサブセクションに一致させます
        section_pattern = rf"==\s*{re.escape(section_title)}\s*==\n(.*?)(?=\n==[^=])"
        section_content = re.search(section_pattern, content, re.S)
        if section_content:
            return section_content.group(1)
        else:
            return "Section not found"
    except:
        return None
       
def get_works_list(text):
    # サブセクションと作品を抽出
    sections = re.findall(r'=== (.+?) ===\n\n([\s\S]*?)(?=\n=== |\Z)', text)

    # サブセクションと作品を格納するための辞書を作成
    subsection_dict = {}

    # 辞書を埋める
    for section in sections:
        subsection_dict[section[0]] = section[1]
    
    # 各セクションごとにパターンを削除
    for section, works_text in subsection_dict.items():
        # パターンを削除
        cleaned_works = [re.sub(r"\[\[|\]\]|\[\[.*?\|", "", re.sub(r"<ref>.*?</ref>", "", re.sub(r"''", "", line.strip('*').strip()))) for line in works_text.split('\n') if line.strip()]
        subsection_dict[section] = cleaned_works
    
    # 結果を返す
    return subsection_dict

def get_work_info(page_title, page_content):
    # 各情報を抽出
    author_match = re.search(r'\| *author *= *\[\[([^|]+)\|?.*?\]\]', page_content)
    country_match = re.search(r'\| *country *= *([^|\n]+)', page_content)
    language_match = re.search(r'\| *language *= *([^|\n]+)', page_content)
    publisher_match = re.search(r'\| *publisher *= *\[\[([^|]+)\|?.*?\]\]', page_content)
    release_date_match = re.search(r'\| *release_date *= *([^|\n]+)', page_content)
    
    # 作品情報の辞書を初期化
    work_info = {
        "title": page_title,
        "author": None,
        "publication_year": None,
        "country": None,
        "language": None,
        "publisher": None,
        "Works": None
    }

    # 正規なページタイトルを取得
    if author_match:
        work_info["author"] = re.sub(r'\]\]', '', author_match.group(1)).strip()
    if country_match:
        work_info["country"] = country_match.group(1).strip()
    if language_match:
        work_info["language"] = language_match.group(1).strip()
    if publisher_match:
        work_info["publisher"] = re.sub(r'\]\]', '', publisher_match.group(1)).strip()
    if release_date_match:
        work_info["publication_year"] = release_date_match.group(1).strip()

    return work_info

def main(page_title):
    # Wikipediaページの情報を取得
    page_content = get_wikipedia_page_info(page_title)
    work_info = get_work_info(page_title, page_content)

    if work_info['author']:
        # Wikipediaページの情報を取得
        author_content = get_wikipedia_section(work_info['author'], "Works")
        other_works = get_works_list(author_content)
        if other_works:
            work_info["Works"] = other_works
    
    for key, value in work_info.items():
        if value is None:
            work_info[key] = "Not specified"
    # ファイルパスを修正
    output_file_path = f"bookinfo/static/json/{page_title}.json"
    
    # 作品情報をJSONファイルに保存
    with open(output_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(work_info, json_file, ensure_ascii=False, indent=4)

    return work_info


