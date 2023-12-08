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
        print(f'gutenbergIDが{gutenbergID}の要約データを{dir_path}に保存しました')


import sys
if __name__=="__main__":
    # コマンドライン引数のチェック
    args = sys.argv
    if len(args) != 2 or not args[1].isdigit():
        print('引数が正しくありません')
        print('使い方')
        print('python summarized_data_handler.py {gutenbergID}')
        exit()

    # 要約データをのパスを求める
    dir_name = os.path.dirname(__file__)
    if not dir_name: dir_name = '.'
    gutenbergID = int(args[1])
    summarized_data_name = 'all_data.json'
    summarized_data_path = f'{dir_name}/{gutenbergID}/sample0/{summarized_data_name}'

    # gutenbergIDが0のときはサンプルデータを作成する
    if gutenbergID == 0:
        my_module = __import__('0.make_all_data')
        my_module.make_all_data.make_all_data(summarized_data_name)

    # summarizedDataHandlerの使い方例
    summarized_data_handler = summarizedDataHandler()
    summarized_data_handler.json_to_dir(summarized_data_path)