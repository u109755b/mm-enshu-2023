from distutils.util import strtobool
import re
import os
import json
import argparse


# titleとscene_group_nameを入力すると, 何個の文章に分かれて保存されているか求めて, その数を返す関数
def find_max_split_idx(title, scene_group_name):
    dir_files = os.listdir(f"log/{title}/{scene_group_name}")
    split_idxs = []
    file_pattern = re.compile(f"body_scene(\d+)\.txt")
    for file in dir_files:
        try:
            split_idxs.append(int(re.findall(file_pattern, file)[0]))
        except:
            pass
    
    return max(split_idxs)+1


# tgt_item(node, edge)が登場した場面を求める関数
def find_appear_split(tgt_item, raw_items):
    result_split_idxs = []
    for split_idx, raw_item in enumerate(raw_items):
        if tgt_item in raw_item:
            result_split_idxs.append(split_idx)
    
    return result_split_idxs


# jsonに保存するsummaryをjson_summaryにまとめる関数
def make_json_summary(title, scene_group_name, max_split_idx):
    # jsonに保存するsummary情報を格納
    json_summary = []

    # summary, scene_infoの読み込み
    with open(f"log/{title}/{scene_group_name}/summary.txt", encoding="utf-8") as f:
        summaries = f.read().split("\n")
    with open(f"log/{title}/{scene_group_name}/scene_info.txt", encoding="utf-8") as f:
        scene_infos = f.read().split("\n")

    # summaryの追加
    json_summary = [
        f"<p><b>{split_idx + 1}. {scene_infos[split_idx]}</b><br>{summaries[split_idx]}</p>" 
        for split_idx in range(max_split_idx)
    ]

    return json_summary


# jsonに保存するnode情報をjson_nodesにまとめる関数
# TODO: node_title(ノードの詳細情報), node_group(ノードの分類)を追加 *5から修正する必要がある
def make_json_nodes(title, scene_group_name, max_split_idx):
    # jsonに保存するnode情報を格納
    json_nodes = []

    # nodeの読み込み
    raw_nodes_list = []
    for split_idx in range(max_split_idx):
        with open(f"log/{title}/{scene_group_name}/node_scene{split_idx}.txt", encoding="utf-8") as f:
            raw_nodes_list.append(f.read().split("\n"))

    # 全てのノード名を収集(登場順を保持)
    all_node_labels = sorted(set(sum(raw_nodes_list, [])), key=sum(raw_nodes_list, []).index)
    for node_label in all_node_labels:
        # node_id, node_label, node_periodを追加
        # node_id: node_labelと同じに設定(id, labelに'を含むとエラーが発生するため, json作成時に'を取り除く)
        # node_period: ノードが登場してから最後の場面までに設定
        # TODO: 適切なnode_periodの設定方法を考案
        json_nodes.append(
            {
                "id": node_label.replace("'", ""),
                "label": node_label.replace("'", ""),
                "period": [split_idx + 1 for split_idx in find_appear_split(node_label, raw_nodes_list)],
                "size": 20,
            }
        )
    
    # jsonに保存するnode情報と, ノードidの集合(=ノードlabelの集合, edge作成に利用)を返す
    return json_nodes, all_node_labels


# jsonに保存するedge情報をjson_edgesにまとめる関数
# TODO: edge_title(エッジの詳細情報)を追加 *5から修正する必要がある
def make_json_edges(title, scene_group_name, max_split_idx, all_node_labels):
    # jsonに保存するedge情報を格納
    json_edges = []

    # edgeの読み込み(読み込み時にカンマの表記揺れを統一)
    raw_edges_list = []
    for split_idx in range(max_split_idx):
        with open(f"log/{title}/{scene_group_name}/edge_scene{split_idx}.txt", encoding="utf-8") as f:
            raw_edges_list.append([re.sub(r"\s*,\s*", r",", raw_edge) for raw_edge in f.read().split("\n")])

    # 全てのラベル表現を収集(登場順を保持)
    # TODO: 複数回登場する同一edgeへの対応(現時点では, 最初に発生したedgeのみを考慮している)
    all_raw_edges = sorted(set(sum(raw_edges_list, [])), key=sum(raw_edges_list, []).index)
    for raw_edge in all_raw_edges:
        edge_from_label, edge_label, edge_to_label = raw_edge.split(",")
        # from, toが共にnodesに登録されている場合のみedge情報を抽出
        if (edge_from_label in all_node_labels) and (edge_to_label in all_node_labels):
            # edge_id, edge_label, edge_to, edge_from, edge_periodを追加
            # edge_id: raw_edgeと同じに設定(現時点では, 最初に発生したedgeのみを考慮している)
            # edge_period: エッジが登場した場面のみに設定
            json_edges.append(
                {
                    "id": raw_edge.replace("'", ""),
                    "label": edge_label.replace("'", ""),
                    "from": edge_from_label.replace("'", ""),
                    "to": edge_to_label.replace("'", ""),
                    "arrows": "to",
                    "period": [split_idx + 1 for split_idx in find_appear_split(raw_edge, raw_edges_list)],
                }
            )
    
    return json_edges


# 使われていないノードを削除する関数
def remove_unused_nodes(json_dict):
    new_json_dict = {}
    
    # ノードを順番に確認し, 使われているノードを格納していく
    new_json_nodes = []
    for node_dict in json_dict["nodes"]:
        # このノードのperiodを更新する
        new_node_periods = []
        # このノードがあるperiodでedgesから参照されている場合, このperiodをnew_node_periodsに追加する
        for node_period in node_dict["period"]:
            # 全てのedgeについて, このノードを参照しているかどうか確認していく
            for edge_dict in json_dict["edges"]:
                if (
                    (node_period in edge_dict["period"]) and 
                    (node_dict["id"] == edge_dict["from"] or node_dict["id"] == edge_dict["to"])
                ):
                    new_node_periods.append(node_period)
                    break
        
        # new_node_periodsが空ではない場合, このノードは使われている
        if new_node_periods:
            new_json_nodes.append(
                {
                    "id": node_dict["id"],
                    "label": node_dict["label"],
                    "period": new_node_periods,
                    "size": node_dict["size"]
                }
            )
    
    # json_dictを更新する
    new_json_dict["title"] = json_dict["title"]
    new_json_dict["summary"] = json_dict["summary"]
    new_json_dict["nodes"] = new_json_nodes
    new_json_dict["edges"] = json_dict["edges"]

    return new_json_dict


# from, to, periodが同じedgeを統合する関数
# 統合後のlabelは最後に登場するlabelに設定し, 統合後のtitleは全てのtitleを"&"で繋いだものとする
# TODO: より良い統合方法の作成 *5から修正する必要がある
def integrate_same_from_to_period_edges(json_dict, max_split_idx):
    # json_dict["edges"]のうち, ユニークなfromとtoを収集
    unique_from_to_ids = set()
    for edge in json_dict["edges"]:
        from_to_id = (edge["from"], edge["to"])
        unique_from_to_ids.add(from_to_id)

    # uniqueなfromとtoについて, 各periodで登場するか確認していき, 登場する場合一つのedgeにまとめる
    unique_json_edges = []
    for unique_from_to_id in unique_from_to_ids:
        unique_from, unique_to = unique_from_to_id
        # 注意: periodは1から始まる
        for period in range(1, max_split_idx+1):
            # 全てのedgeを確認して, from, to, periodが同じものをリストに追加していく
            same_from_to_period_edges = []
            for edge in json_dict["edges"]:
                if (edge["from"] == unique_from) and (edge["to"] == unique_to) and (period in edge["period"]):
                    same_from_to_period_edges.append(edge)
            
            # リストに追加されている場合, 新しいedgesに追加
            # labelの内容は最後に登場したedgeと同じにして, titleの内容は各edgeの内容を"&"で繋いだものとする
            if same_from_to_period_edges:
                unique_json_edges.append(
                    {
                        "id": f"{unique_from}to{unique_to}_{period}",
                        "label": same_from_to_period_edges[-1]["label"],
                        "title": " & ".join(
                                [
                                    same_from_to_period_edge["label"] 
                                    for same_from_to_period_edge in same_from_to_period_edges
                                ]
                            ),
                        "from": unique_from,
                        "to": unique_to,
                        "arrows": "to",
                        "period": [period],
                    }
                )

    json_dict["edges"] = unique_json_edges

    return json_dict


def main():
    # 設定
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

    scene_group_names = ["location"] * use_location + ["time"] * use_time + ["character"] * use_character
    scene_group_name = "_".join(scene_group_names)
    max_split_idx = find_max_split_idx(title, scene_group_name)

    # すでに実行済みの場合, 実行しない
    if os.path.exists(f"log/{title}/{scene_group_name}/graph.json"):
        print("json file has already existed!")
        exit()

    # 要約が存在しない場合, 先に4_summarize_splited_body.pyを実行するように促す
    if not os.path.exists(f"log/{title}/{scene_group_name}/summary.txt"):
        print("Summary doesn't exist!")
        print(
            f"Please run 'python 4_summarize_splited_body.py --title {title}"
            f" --use_location {use_location} --use_time {use_time} --use_character {use_character}'"
        )
    
    # ノード, エッジが存在しない場合, 先に5_create_knowledge_graph.pyを実行するように促す
    if not os.path.exists(f"log/{title}/{scene_group_name}/node_scene0.txt"):
        print("Knowledge graph doesn't exist!")
        print(
            f"Please run 'python 5_create_knowledge_graph.py --title {title}"
            f" --use_location {use_location} --use_time {use_time} --use_character {use_character}'"
        )
    

    # jsonファイルの作成
    json_dict = {}

    # titleの追加
    json_dict["title"] = title

    # summaryの追加
    json_dict["summary"] = make_json_summary(title, scene_group_name, max_split_idx)

    # nodesの追加
    json_nodes, all_node_labels = make_json_nodes(title, scene_group_name, max_split_idx)
    json_dict["nodes"] = json_nodes

    # edgesの追加
    json_dict["edges"] = make_json_edges(title, scene_group_name, max_split_idx, all_node_labels)

    # 使われていないnodesの削除
    json_dict = remove_unused_nodes(json_dict)

    # from, to, periodが同じedgesの統合
    json_dict = integrate_same_from_to_period_edges(json_dict, )

    # jsonファイルの保存
    with open(f"log/{title}/{scene_group_name}/graph.json", "w", encoding="utf-8") as f:
        json.dump(json_dict, f, indent=4)
    

if __name__ == "__main__":
    main()
