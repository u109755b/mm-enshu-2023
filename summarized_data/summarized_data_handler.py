import os
import shutil
import json
import re


# 要約データを階層的にファイル保存する
class summarizedDataHandler:
    def __init__(self):
        pass

    # 再帰的にデータを保存する
    def _to_dir_rec(self, dir_path, section_data):
        make_valid_filename = lambda filename: re.sub(r'[\/:*?"<>| ]', '_', filename)
        for i, section in enumerate(section_data):
            id = i+1
            section_name = make_valid_filename(section['sectionName'])
            # フォルダ作成
            if 'subSection' in section:
                section_path = f'{dir_path}/{id}__{section_name}'
                os.makedirs(section_path, exist_ok=True)
                with open(f'{section_path}/0__section_name.txt', 'w', encoding='utf-8') as f:
                    f.write(section['sectionName'])
                self._to_dir_rec(section_path, section['subSection'])
            # 各章の要約データ保存
            else:
                with open(f'{dir_path}/{id}__{section_name}.json', 'w', encoding='utf-8') as f:
                    json.dump(section, f, indent=4, ensure_ascii=False)

    # json形式の要約データをディレクトリ構造で保存して見やすくする
    def json_to_dir(self, summarized_data_path):
        with open(summarized_data_path, encoding='utf-8') as f:
            summarized_data = json.load(f)
        parent_folder = os.path.dirname(summarized_data_path)
        dir_path = f'{parent_folder}/directory_data'
        os.makedirs(dir_path, exist_ok=True)
        shutil.rmtree(dir_path)
        self._to_dir_rec(dir_path, summarized_data)
        print(f'{gutenbergID}の要約データを{dir_path}に保存しました')



if __name__=="__main__":
    # 三匹の子豚サンプルデータの各章の要約データを読み込む
    section_list = ['1-1', '1-2', '2-1', '2-2-1', '2-2-2']
    chapter_data = {}
    for section_name in section_list:
        with open(f'sample_json/{section_name}.json', encoding='utf-8') as f:
            chapter_data[section_name] = json.load(f)

    # ver2の階層的な段落に対応した要約データ
    summarized_data = [
        {
            "sectionName": "第1章 三びきのこぶたの巣立ち",
            "subSection": [
                chapter_data['1-1'],
                chapter_data['1-2'],
            ],
        },
        {
            "sectionName": "第2章 オオカミの登場",
            "subSection": [
                chapter_data['2-1'],
                {
                    "sectionName": "第2.2章 オオカミvs末のこぶた",
                    "subSection": [
                        chapter_data['2-2-1'],
                        chapter_data['2-2-2'],
                    ],
                },
            ],
        },
    ]

    # 要約データを1つのjsonファイルに保存
    gutenbergID = 18155     # The Story of the Three Little Pigs
    summarized_data_name = 'all_data.json'
    summarized_data_path = f'{gutenbergID}/{summarized_data_name}'
    
    os.makedirs(f'{gutenbergID}', exist_ok=True)
    with open(summarized_data_path, 'w', encoding='utf-8') as f:
        json.dump(summarized_data, f, indent=4, ensure_ascii=False)

    # summarizedDataHandlerの使い方例
    summarized_data_handler = summarizedDataHandler()
    summarized_data_handler.json_to_dir(summarized_data_path)