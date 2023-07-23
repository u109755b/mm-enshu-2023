from distutils.util import strtobool
import os
import argparse


# 場面ごとに分類された本文を, 場面ごとに分割して保存する関数
# 分類は2_group_sentence_by_scene.pyで行う
def save_splited_body_by_scene(title, use_location, use_time, use_character):
    # 文単位で分割された本文の読み込み
    sentences = []
    with open(f"log/{title}/body.txt", encoding="utf-8") as f:
        for line in f:
            sentence_idx, sentence = line.strip().split("\t")
            sentences.append(sentence)

    # グループ情報の読み込み
    # groupsにlocation, time, characterの情報の内利用するものを\t区切りで格納
    groups = [""] * len(sentences)
    if use_location:
        with open(f"log/{title}/body_group_by_location.txt", encoding="utf-8") as f:
            for line in f:
                sentence_idx, location_group = line.strip().split("\t")
                groups[int(sentence_idx)] += location_group

    if use_time:
        with open(f"log/{title}/body_group_by_time.txt", encoding="utf-8") as f:
            for line in f:
                sentence_idx, time_group = line.strip().split("\t")
                # groupsが空の場合, time_groupをそのまま追加
                if not use_location:
                    groups[int(sentence_idx)] += time_group
                # groupsが空でない場合, "\t"+time_groupを追加
                else:
                    groups[int(sentence_idx)] += "\t" + time_group

    if use_character:
        with open(f"log/{title}/body_group_by_character.txt", encoding="utf-8") as f:
            for line in f:
                sentence_idx, character_group = line.strip().split("\t")
                # groupsが空の場合, character_groupをそのまま追加
                if not use_location and not use_time:
                    groups[int(sentence_idx)] += character_group
                # groupsが空でない場合, "\t"+character_groupを追加
                else:
                    groups[int(sentence_idx)] += "\t" + character_group


    # splited_linesにグループごとに分割された本文を格納し, splited_lines_group_infoに各グループの情報を格納
    last_group = ""
    splited_line = ""
    splited_lines = []
    splited_lines_group_info = []
    for sentence_idx in range(len(sentences)):
        # 前の文と異なるグループの場合, splited_lines, splited_lines_group_infoを更新し, splited_lineを初期化
        if last_group != groups[sentence_idx]:
            # splited_lineが空の場合追加しない
            splited_lines.append(splited_line.strip()) if splited_line else None
            splited_lines_group_info.append(last_group) if splited_line else None
            splited_line = ""
        # splited_lineに新たな文を追加し, last_groupを更新
        splited_line += " " + sentences[sentence_idx]
        last_group = groups[sentence_idx]

    # 最後の部分をsplited_linesに追加
    splited_lines.append(splited_line.strip())
    splited_lines_group_info.append(last_group)


    # body_splited_by_{scene_group_name}_{split_idx}.txtに分割された本文を格納
    scene_group_names = ["location"] * use_location + ["time"] * use_time + ["character"] * use_character
    scene_group_name = "_".join(scene_group_names)
    for split_idx, splited_line in enumerate(splited_lines):
        with open(f"log/{title}/body_splited_by_{scene_group_name}_{split_idx}.txt", "w", encoding="utf-8") as f:
            f.write(splited_line)
    
    # info_{scene_group_name}.txtにグループ情報を格納
    with open(f"log/{title}/info_{scene_group_name}.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(splited_lines_group_info))


def main():
    # 入力でtitleと分類に利用する場面の種類を指定
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", type=str, default="The Story of the Three Little Pigs")
    parser.add_argument("--use_location", type=str, default="True")
    parser.add_argument("--use_time", type=str, default="False")
    parser.add_argument("--use_character", type=str, default="False")
    args = parser.parse_args()

    title = args.title
    use_location = strtobool(args.use_location)
    use_time = strtobool(args.use_time)
    use_character = strtobool(args.use_character)

    # 既に分割済みの場合, 実行しない
    scene_group_names = ["location"] * use_location + ["time"] * use_time + ["character"] * use_character
    scene_group_name = "_".join(scene_group_names)
    if os.path.exists(f"log/{title}/body_splited_by_{scene_group_name}_0.txt"):
        print("The split result already exists!")
        exit()

    # 2_group_sentence_by_scene.pyでの分類が行われていない場合, 先に実行するように促す
    if use_location and not os.path.exists(f"log/{title}/body_group_by_location.txt"):
        print("Grouping result doesn't exist!")
        print(f"Please run 'python 2_group_sentence_by_scene.py --title {title} --scene_type location'")
    
    if use_time and not os.path.exists(f"log/{title}/body_group_by_time.txt"):
        print("Grouping result doesn't exist!")
        print(f"Please run 'python 2_group_sentence_by_scene.py --title {title} --scene_type time'")
    
    if use_character and not os.path.exists(f"log/{title}/body_group_by_character.txt"):
        print("Grouping result doesn't exist!")
        print(f"Please run 'python 2_group_sentence_by_scene.py --title {title} --scene_type character'")



    # 場面ごとに分類された本文を, 場面ごとに分割して保存する
    save_splited_body_by_scene(title, use_location, use_time, use_character)


if __name__ == "__main__":
    main()
