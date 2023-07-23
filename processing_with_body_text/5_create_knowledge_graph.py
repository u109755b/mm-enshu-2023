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


# ある文章について, 初めてNode, Edgeを作成する場合の指示を作成
def make_first_instruct(output_type, splited_body, existed_nodes=[]):
    # nodeを作成する場合の指示
    if output_type == "node":
        first_instruct = (
            "I want to make a knowledge graph about this sentences.\n"
            "Please output the nodes that appear in the knowledge graph as much as possible.\n"
            "Please output in the following format.\n\n"
            "Example\n"
            "'''\n- The first Pig\n- The second Pig\n- A Wolf\n'''\n\n"
            "Sentence\n"
            f"'''\n{splited_body}\n'''"
        )
    # edgeを作成する場合の指示: これまでに出力したノードを制約として加える
    elif output_type == "edge":
        first_instruct = (
            "I want to make a knowledge graph about this sentences.\n"
            "Please output the edges that appear in the knowledge graph.\n"
            "Please output in the following format.\n\n"
            "Constraint\n"
            f"'''\n- You must select the nodes of the knowledge graph from '{', '.join(existed_nodes)}'\n"
            "- The format of the edge is 'node-1, relation between node-1 and node-2, node-2'\n'''\n\n"
            "Example\n"
            "'''\n- A Wolf, eat, The first Pig\n- A Wolf, declare to eat, The third Pig\n'''\n\n"
            "Sentence\n"
            f"'''\n{splited_body}\n'''"
        )

    return first_instruct


# EdgeGPTの出力からNode, Edgeを取り出してファイルに保存する関数
# Nodeの場合, outputs(=Node集合)を返す
def save_extracted_outputs(response, title, scene_group_name, split_idx, output_type):
    # EdgeGPTの出力からoutput(node or edge)を取り出す
    outputs = []
    for response_line in response["text"].split("\n"):
        try:
            output = re.findall(r"- (.*)", response_line)[0]
            # Nodeの場合, そのまま追加
            if output_type == "node":
                outputs.append(output)
            # Edgeの場合, ","が2つ含まれているもののみを追加
            elif (output_type == "edge") and (len(output.split(",")) == 3):
                outputs.append(output)
        except:
            pass
    
    # 出力を保存
    with open(f"log/{title}/{output_type}_splited_by_{scene_group_name}_{split_idx}.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(outputs))
    
    # nodeの場合, node集合を返す
    if output_type == "node":
        return outputs


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

    # すでに実行済みの場合, 実行しない
    if os.path.exists(f"log/{title}/node_splited_by_{scene_group_name}_0.txt"):
        print("Knowledge graph has already existed!")
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
    

    # Node, Edgeの抽出
    # これまでに出てきたノードを場面ごとに格納し, Edgeの作成に利用
    nodes_list = []
    for split_idx, splited_body in enumerate(splited_bodys):
        # Nodeについて質問する
        # TODO: 対応しない形式の出力が発生した場合, 対応を考える
        prompt = make_first_instruct("node", splited_body)
        print(f"Asking for the following prompts...\n{prompt}\n") if is_show_log else None
        response = await bot.ask(prompt=prompt, conversation_style=ConversationStyle.creative, simplify_response=True)
        print(f"Get the following response!\n{response['text']}\n") if is_show_log else None

        # Nodeを取り出してファイルに保存する
        new_nodes = save_extracted_outputs(response, title, scene_group_name, split_idx, "node")
        # これまでに出てきたノードを更新
        nodes_list.append(new_nodes)
        existed_nodes = sorted(set(sum(nodes_list, [])), key=sum(nodes_list, []).index)

        # Egdeについて質問する(出力Nodeはこれまでに出てきたノードに限定するように指示)
        # TODO: 対応しない形式の出力が発生した場合, 対応を考える
        prompt = make_first_instruct("edge", splited_body, existed_nodes)
        print(f"Asking for the following prompts...\n{prompt}\n") if is_show_log else None
        response = await bot.ask(prompt=prompt, conversation_style=ConversationStyle.creative, simplify_response=True)
        print(f"Get the following response!\n{response['text']}\n") if is_show_log else None

        # Edgeを取り出してファイルに保存する
        save_extracted_outputs(response, title, scene_group_name, split_idx, "edge")
    
    await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
