# storyID を入力すると各場面の本文の要約をファイルに保存する

import argparse
import os
import re
from openai import OpenAI

# key は各自で指定
client = OpenAI(api_key="YOUR API KEY")
gpt_model = "gpt-4-1106-preview"


# storyID を入力すると, 何個の文章に分かれて保存されているか求めてその数を返す関数
def get_scene_num(storyID):
    dir_files = os.listdir(f"log/{storyID}")
    split_idxs = []
    file_pattern = re.compile(f"body_scene(\d+)\.txt")
    for file in dir_files:
        try:
            split_idxs.append(int(re.findall(file_pattern, file)[0]))
        except:
            pass
    
    return max(split_idxs)+1


# storyID を入力すると, 各場面の要約を作成し summary.txt にまとめて保存する関数
def summarization(storyID, show_log):
    # 分割結果の読み込み
    scene_num = get_scene_num(storyID)
    split_bodys = []
    for split_idx in range(scene_num):
        with open(f"log/{storyID}/body_scene{split_idx}.txt", encoding="utf-8") as f:
            split_bodys.append(f.read())

    # 要約の実行
    summaries = []
    for split_body in split_bodys:
        # プロンプトの作成
        chat_messages = [
            {"role": "system", "content": "Only answer what you have been instructed to output."},
            {"role": "user", "content": f"Summarize the following Sentences and output the results.\nSentences: {split_body}"},
        ]

        # chatGPT にプロンプトを投げる
        print(f"Asking for the following prompts...\n{chat_messages}\n") if show_log else None
        response = client.chat.completions.create(model = gpt_model, messages = chat_messages)
        print(f"Get the following response!\n{response}\n") if show_log else None

        # 要約の抽出
        summary = response.choices[0].message.content.replace("\n", " ")
        summaries.append(summary)

        print(f"original text: {len(split_body.split())} words, summary: {len(summary.split())} words, Compression ratio: {int(len(summary.split())/len(split_body.split())*100)}%\n") if show_log else None
    
    # 要約結果を"log/{storyID}/summary.txt"に保存
    with open(f"log/{storyID}/summary.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(summaries))


def main():
    # 入力で storyID を指定
    parser = argparse.ArgumentParser()
    parser.add_argument("--storyID", type=int)
    parser.add_argument("--show_log", action="store_true")
    args = parser.parse_args()

    storyID = args.storyID
    show_log = args.show_log

    # すでに要約済みの場合, 実行しない
    if os.path.exists(f"log/{storyID}/summary.txt"):
        print("Summary has already existed!")
        exit()
    
    # 分割済みの本文が存在しない場合, 先に 1_preprocess_txt.py を実行するように促す
    if not os.path.exists(f"log/{storyID}/body_scene0.txt"):
        print("The splited text doesn't exist!")
        print(f"Please run 'python 1_preprocess_txt.py --storyID {storyID}")


    # 各場面の要約を作成し, summary.txt に保存する
    summarization(storyID, show_log)


if __name__ == "__main__":
    main()
