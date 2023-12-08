import os
import json

def make_all_data(summarized_data_name):
    dir_name = os.path.dirname(__file__)
    if not dir_name: dir_name = '.'

    # 三匹の子豚サンプルデータの各章の要約データを読み込む
    section_list = ['1-1', '1-2', '2-1', '2-2-1', '2-2-2']
    chapter_data = {}
    for section_name in section_list:
        with open(f'{dir_name}/sample_json/{section_name}.json', encoding='utf-8') as f:
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

    os.makedirs(f'{dir_name}/sample0', exist_ok=True)
    with open(f'{dir_name}/sample0/{summarized_data_name}', 'w', encoding='utf-8') as f:
        json.dump(summarized_data, f, indent=4, ensure_ascii=False)

    print('sampleのall_data.jsonを作成しました')


if __name__=="__main__":
    make_all_data()