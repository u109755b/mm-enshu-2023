import os, glob
import json
import re

summarized_data_dir = 'visualizer/static/visualizer/summarized_data'
title_file_name = 'title.txt'
sample_id_pattern = re.compile(r'^sample\d+$')
all_data_file_name = 'all_data.json'

# ファイルの読み書き
def read_txt(path):
    with open(path, encoding='utf-8') as f:
        return f.read()

def read_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def save_txt(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(data)

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def save_image(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(data)

# 要約データが存在する物語のgutenbergIDのリストを作成する
def get_gutenbergIDs():
    gutenbergIDs = []
    story_data_folders = glob.glob(f'{summarized_data_dir}/*')
    for story_data_folder in story_data_folders:
        gutenbergID = story_data_folder.split('/')[-1]
        if not gutenbergID.isdecimal(): continue
        gutenbergIDs.append(gutenbergID)
    return sorted(gutenbergIDs)

# 指定された物語のtitleを返す
def get_title(gutenbergID):
    return read_txt(f'{summarized_data_dir}/{gutenbergID}/{title_file_name}')

# 指定された物語のsample_id_listを返す
def get_sample_id_list(gutenbergID):
    sample_id_list = []
    sample_dir_names = glob.glob(f'{summarized_data_dir}/{gutenbergID}/*')
    for sample_dir_name in sample_dir_names:
        sample_id = sample_dir_name.split('/')[-1]
        if not sample_id_pattern.match(sample_id): continue
        sample_id_list.append(sample_id)
    sample_id_list.sort()
    return sample_id_list

# 指定された物語のsection_dataを返す
def get_section_data(gutenbergID, sample_id):
    return read_json(f'{summarized_data_dir}/{gutenbergID}/{sample_id}/{all_data_file_name}')

# 指定された物語のchapter_id_listを返す
def _get_chapter_id_list(section_data, depth=0, parent_id=[]):
    chapter_id_list = []
    for i, section in enumerate(section_data):
        num = i+1
        parent_id.append(str(num))
        if 'subSection' not in section:
            chapter_id_list.append('-'.join(parent_id))
        else:
            sub_chapter_id_list = _get_chapter_id_list(section['subSection'], depth+1, parent_id)
            chapter_id_list.extend(sub_chapter_id_list)
        parent_id.pop()
    return chapter_id_list
def get_chapter_id_list(gutenbergID, sample_id):
    section_data = get_section_data(gutenbergID, sample_id)
    return _get_chapter_id_list(section_data)