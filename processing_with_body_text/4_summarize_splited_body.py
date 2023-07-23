from EdgeGPT.EdgeGPT import Chatbot, ConversationStyle
from distutils.util import strtobool
import re
import os
import json
import asyncio
import argparse


# titleとscene_group_nameを入力すると, 何個の文章に分かれて保存されているか求めて, その数を返す関数
def find_max_split_idx(title, scene_group_name):
    dir_files = os.listdir(f"log/{title}")
    split_idxs = []
    file_pattern = re.compile(f"body_splited_by_{scene_group_name}_(\d+)\.txt")
    for file in dir_files:
        try:
            split_idxs.append(int(re.findall(file_pattern, file)[0]))
        except:
            pass
    
    return max(split_idxs)+1


async def main():
    # 設定
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", type=str, default="The Story of the Three Little Pigs")
    parser.add_argument("--use_location", type=str, default="True")
    parser.add_argument("--use_time", type=str, default="False")
    parser.add_argument("--use_character", type=str, default="False")
    parser.add_argument("--is_show_log", type=str, default="False")
    args = parser.parse_args()

    title = args.title
    use_location = strtobool(args.use_location)
    use_time = strtobool(args.use_time)
    use_character = strtobool(args.use_character)
    is_show_log = strtobool(args.is_show_log)

    scene_group_names = ["location"] * use_location + ["time"] * use_time + ["character"] * use_character
    scene_group_name = "_".join(scene_group_names)

    # すでに要約済みの場合, 実行しない
    if os.path.exists(f"log/{title}/summary_splited_by_{scene_group_name}.txt"):
        print("Summary has already existed!")
        exit()
    
    # 分割済みの本文が存在しない場合, 先に3_split_body_by_scene.pyを実行するように促す
    if not os.path.exists(f"log/{title}/body_splited_by_{scene_group_name}_0.txt"):
        print("The splited text doesn't exist!")
        print(
            f"Please run 'python 3_split_body_by_scene.py --title {title}"
            f" --use_location {use_location} --use_time {use_time} --use_character {use_character}'"
        )
    
    # EdgeGPTの設定
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cookie_path = os.path.join(script_dir, 'bing_cookies_.json')
    cookies = json.loads(open(cookie_path, encoding="utf-8").read())
    bot = await Chatbot.create(cookies=cookies)


    # 分割結果の読み込み
    max_split_idx = find_max_split_idx(title, scene_group_name)
    splited_bodys = []
    for split_idx in range(max_split_idx):
        with open(f"log/{title}/body_splited_by_{scene_group_name}_{split_idx}.txt", encoding="utf-8") as f:
            splited_bodys.append(f.read())


    # 要約の実行
    # ある文章について, 初めて要約を行う場合の指示
    first_instruct = (
        "I want to summarize this sentences.\n"
        "Please output in the specified format.\n"
        "Example\n'''\n- Summary: ~~~\n'''\n"
    )

    summaries = []
    for splited_body in splited_bodys:
        prompt = first_instruct + splited_body
        print(f"Asking for the following prompts...\n{prompt}\n") if is_show_log else None
        response = await bot.ask(prompt=prompt, conversation_style=ConversationStyle.creative, simplify_response=True)
        print(f"Get the following response!\n{response['text']}\n") if is_show_log else None

        # 要約を取り出す (対応形式 - Summary: "summary")
        # TODO: 対応しない形式の出力が発生した場合, 対応を考える
        summary = response["text"].split("- Summary: ")[-1]
        summaries.append(summary)

    
    # 要約結果を"log/{title}/summary_splited_by_{scene_group_name}.txt"にまとめる
    with open(f"log/{title}/summary_splited_by_{scene_group_name}.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(summaries))
    

    await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
