# storyID を入力すると各場面の node, edge をファイルに保存する
# sceneID で指定された場面のみを対象とする
# TODO: プロンプトの改良

import argparse
import os
import re
from openai import OpenAI

# keyは各自で指定
client = OpenAI(api_key="YOUR API KEY")
gpt_model = "gpt-4-1106-preview"


# storyID を入力すると, 何個の文章に分かれて保存されているか求めてその数を返す関数
# TODO: utils.py などを作成し共通の関数をまとめる
def get_scene_num(storyID):
    dir_files = os.listdir(f"log/{storyID}")
    sceneIDs = []
    file_pattern = re.compile(f"body_scene(\d+)\.txt")
    for file in dir_files:
        try:
            sceneIDs.append(int(re.findall(file_pattern, file)[0]))
        except:
            pass
    
    return max(sceneIDs)+1


# ChatGPT の出力から node, edge を取り出してファイルに保存する関数
# node の場合, 登場人物名のリストを返す
def reshape_responce(response, storyID, sceneID, output_type):
    outputs = []        # response から取り出した node or edge の情報
    characters = []     # node の場合, 登場人物名を保存
    edge_flag = 0       # edge の場合, 最終結果かどうか区別するフラグを利用
    for response_line in response.choices[0].message.content.split("\n"):
        # edge の場合, Step 4 の行の後に最終結果が表示される
        if re.findall(r"Step 4", response_line, flags=re.IGNORECASE):
            edge_flag = 1
        
        # node, edge の表示形式は "- ~~" or "\d+. ~~"
        if re.findall(r"\d+. (.*)", response_line):
            output = re.findall(r"\d+. (.*)", response_line)[0]
        elif re.findall(r"- (.*)", response_line):
            output = re.findall(r"- (.*)", response_line)[0]
        else:
            continue
        
        # Nodeの場合, "," が2つ以上含まれているものを追加し, 登場人物名を追加
        if (output_type == "node") and (len(output.split(",")) > 2):
            outputs.append(output)
            characters.append(output.split(",")[0])
        # Edgeの場合, edge_flag==1 かつ "," が3つ以上含まれているものを追加
        elif (output_type == "edge") and (len(output.split(",")) > 3) and edge_flag:
            outputs.append(output)
    
    # 出力を保存
    with open(f"log/{storyID}/{output_type}_scene{sceneID}.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(outputs))
    
    # node の場合, node 集合を返す
    if output_type == "node":
        return characters


# storyID を入力すると, 各場面の node, edge を抽出してファイルに保存する関数
# TODO: プロンプトの改良
def create_knowledge_graph_one_scene(storyID, sceneID, show_log):
    # 分割結果の読み込み
    with open(f"log/{storyID}/body_scene{sceneID}.txt", encoding="utf-8") as f:
        scene_body = f.read()

    # トークン数を記録
    prompt_tokens, completion_tokens = 0, 0

    # node, edge の抽出
    # node 抽出用プロンプトの作成
    node_user_message = (
        "I want to make a knowledge graph of the characters about following sentences.\n"
        "Please output the nodes that appear in the knowledge graph as much as possible.\n"
        "Also, please give a summary of each character and its importance.\n"
        "Please output in the following format.\n\n"
        "Constraints\n"
        "'''\n- You must not output any nodes other than the characters, such as places, tools, etc.\n'''\n\n"
        "Format\n"
        "'''\n- Name of each character, Summary of each character, Importance of each character (real number from 0 to 1)'''\n\n"
        "Example\n"
        "'''- Old Sow, The mother of the three little pigs, 0.2'''\n\n"
        "Sentence\n"
        f"'''\n{scene_body}\n'''"
    )

    node_messages = [
        {"role": "system", "content": "Only answer what you have been instructed to output."},
        {"role": "user", "content": node_user_message},
    ]

    # chatGPT にプロンプトを投げる
    print(f"Asking for the following prompts...\n{node_messages}\n") if show_log else None
    response = client.chat.completions.create(model = gpt_model, messages = node_messages)
    print(f"Get the following response!\n{response}\n") if show_log else None
    prompt_tokens += response.usage.prompt_tokens
    completion_tokens += response.usage.completion_tokens

    # ノードの抽出, 保存
    nodes = reshape_responce(response, storyID, sceneID, "node")


    # edge 抽出用プロンプトの作成
    nodes_str = ", ".join(nodes)

    edge_user_message = (
        "I want to create a knowledge graph of the characters about the following sentence.\n"
        "Please find and output the edges that appear in the knowledge graph step by step based on the following Steps.\n\n"
        "Steps\n"
        "'''\n"
        "- Step 1: Find as many edges as possible that appear in the sentence and summarize them according to the Format.\n"
        f"- Step 2: Extract only the edges where both input and output nodes are included in '{nodes_str}'.\n"
        "- Step 3: Find edges that have the same input and output node pairs and merge the edge contents into a single edge.\n"
        "- Step 4: Check carefully whether the Constraints are satisfied, and output the edges that satisfy the constraints.\n"
        "'''\n\n"
        "Constraints\n"
        "'''\n"
        f"- The input and output nodes of an edge must be one of '{nodes_str}'\n"
        "- The knowledge graph must contain only one edge whose input-output node pairs are the same.\n"
        "'''\n\n"
        "Format\n"
        "'''\n"
        "- input node, output node, overview of relationship between input and output node, details of relationship between input and output node\n"
        "'''\n\n"
        "Example\n"
        "'''\n"
        "- A Wolf, The first Pig, eat, A wolf blew the first Pig's house in and ate the first Pig.\n"
        "- The second Pig, Man with furze, ask, The second Pig asked a Man with furze to give him the furze to build a house.\n"
        "'''\n\n"
        "Sentence\n"
        f"'''\n{scene_body}\n'''"
    )

    edge_messages = [
        {"role": "system", "content": "Please answer the output results for each step."},
        {"role": "user", "content": edge_user_message},
    ]

    # chatGPT にプロンプトを投げる
    print(f"Asking for the following prompts...\n{edge_messages}\n") if show_log else None
    response = client.chat.completions.create(model = gpt_model, messages = edge_messages)
    print(f"Get the following response!\n{response}\n") if show_log else None
    prompt_tokens += response.usage.prompt_tokens
    completion_tokens += response.usage.completion_tokens

    # エッジの抽出, 保存
    reshape_responce(response, storyID, sceneID, "edge")
    
    print(f"total prompt tokens: {prompt_tokens}, total completion tokens: {completion_tokens}")


def main():
    # 入力で storyID を指定
    parser = argparse.ArgumentParser()
    parser.add_argument("--storyID", type=int)
    parser.add_argument("--sceneID", type=int)
    parser.add_argument("--show_log", action="store_true")
    args = parser.parse_args()

    storyID = args.storyID
    sceneID = args.sceneID
    show_log = args.show_log

    # すでに実行済みの場合, 実行しない
    if os.path.exists(f"log/{storyID}/node_scene{sceneID}.txt"):
        print("Knowledge graph has already existed!")
        exit()
    
    # 分割済みの本文が存在しない場合, 先に 1_preprocess_txt.pyを実行するように促す
    if not os.path.exists(f"log/{storyID}/body_scene{sceneID}.txt"):
        print("The spliteded text doesn't exist!")
        print(f"Please run 'python 1_preprocess_txt.py --storyID {storyID}")

    
    # 各場面の知識グラフを作成し, node, edge をファイルに保存する
    create_knowledge_graph_one_scene(storyID, sceneID, show_log)


if __name__ == "__main__":
    main()
