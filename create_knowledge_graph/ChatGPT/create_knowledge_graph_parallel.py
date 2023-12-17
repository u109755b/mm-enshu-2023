# storyID を入力すると各場面の node, edge をファイルに保存する
# scene_startID, scene_endID で場面の範囲を指定可能
# すべての場面を並列で実行
import argparse
import os
import re
from tqdm import tqdm
from openai import OpenAI
from chatgpt_utils import get_scene_num, GPT_KEY, GPT_MODEL
from create_knowledge_graph import reshape_responce, create_knowledge_graph_one_scene
from multiprocessing import Pool

client = OpenAI(api_key=GPT_KEY)
gpt_model = GPT_MODEL


def wrapper(args):
    storyID, sceneID, show_log = args
    return create_knowledge_graph_one_scene(storyID, sceneID, show_log)


def main():
    # 入力で storyID を指定
    parser = argparse.ArgumentParser()
    parser.add_argument("--storyID", type=int)
    parser.add_argument("--scene_startID", type=int, default=0, help="どの場面から知識グラフを作成し始めるか指定")
    parser.add_argument("--scene_endID", type=int, default=-1, help="どの場面まで知識グラフを作成し始めるか指定")
    parser.add_argument("--show_log", action="store_true")
    args = parser.parse_args()

    storyID = args.storyID
    scene_startID = args.scene_startID
    scene_endID = args.scene_endID
    show_log = args.show_log

    # scene_endID を指定しない場合, 最後の場面まで知識グラフを作成する
    if scene_endID == -1:
        scene_endID = get_scene_num(storyID)
    else:
        scene_endID += 1

    # すでに実行済みの場合, 実行しない
    if os.path.exists(f"log/{storyID}/node_scene{scene_startID}.txt"):
        print("Knowledge graph has already existed!")
        exit()
    
    # 分割済みの本文が存在しない場合, 先に 1_preprocess_txt.pyを実行するように促す
    if not os.path.exists(f"log/{storyID}/body_scene{scene_startID}.txt"):
        print("The spliteded text doesn't exist!")
        print(f"Please run 'python 1_preprocess_txt.py --storyID {storyID}")

    
    # 各場面の知識グラフを作成し, node, edge をファイルに保存する
    tasks = [(storyID, sceneID, show_log) for sceneID in range(scene_startID, scene_endID)]
    num_processes = scene_endID - scene_startID + 1
    with Pool(num_processes) as p:
        p.map(wrapper, tasks)


if __name__ == "__main__":
    main()
