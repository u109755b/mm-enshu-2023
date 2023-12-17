# storyID を入力すると各場面の本文の要約をファイルに保存する
import argparse
import os
import re
from openai import OpenAI
from chatgpt_utils import get_scene_num, GPT_KEY, GPT_MODEL

client = OpenAI(api_key=GPT_KEY)
gpt_model = GPT_MODEL


# storyID, sceneID を入力すると, 場面の要約を作成し返す関数
def summarize_one_scene(storyID, sceneID, show_log):
    # 分割結果の読み込み
    with open(f"log/{storyID}/body_scene{sceneID}.txt", encoding="utf-8") as f:
        scene_body = f.read()

    # 要約の実行    
    # プロンプトの作成
    chat_messages = [
        {"role": "system", "content": "Only answer what you have been instructed to output."},
        {"role": "user", "content": f"Summarize the following Sentences and output the results.\nSentences: {scene_body}"},
    ]

    # chatGPT にプロンプトを投げる
    print(f"Asking for the following prompts...\n{chat_messages}\n") if show_log else None
    response = client.chat.completions.create(model = gpt_model, messages = chat_messages)
    print(f"Get the following response!\n{response}\n") if show_log else None

    # 要約の抽出
    summary = response.choices[0].message.content.replace("\n", " ")

    print(f"original text: {len(scene_body.split())} words, summary: {len(summary.split())} words, Compression ratio: {int(len(summary.split())/len(scene_body.split())*100)}%\n") if show_log else None
    
    return summary


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
    summaries = []
    scene_num = get_scene_num(storyID)
    for sceneID in range(scene_num):
        summaries.append(summarize_one_scene(storyID, sceneID, show_log))

    with open(f"log/{storyID}/summary.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(summaries))


if __name__ == "__main__":
    main()
