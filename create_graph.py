from mm_enshu_2023_download import ChatbotPrompter
import json
import re
import os
import asyncio
import argparse
import random
import subprocess

MIN_SIZE = 15
SIZE_RANGE = 20

def return_json_dict(args, log_dir=None):
    if log_dir is None:
        log_dir = f'log/{args.title}/'
        
    json_dict = {}
    json_dict['title'] = args.title
    

    nodes_list = []
    label_to_index = {}
    
    # extract node ids and labels
    all_node_list = extract_nodes_from_file(log_dir + 'node.txt')
    for i, node in enumerate(all_node_list):
        label_to_index[node] = i
        nodes_list.append({'id': 'node' + str(i), 'label': node })
    
    # TODO:画像の出力を絵本風や漫画風などと制御できるようにする．
    if args.show_image == True:
        if check_files(f'log/{args.title}', '.jpeg') == False:
            print('Downloading Images...')
            for node in all_node_list:
                prompt = f'{args.title}というタイトルにでてくる{node}の画像を教えてださい．'
                output_dir = f'log/{args.title}/{node}/'
                script_dir = os.path.dirname(os.path.abspath(__file__))
                cookie_path = script_dir + '/cookies.json'
                command = ['python', '-m', 'EdgeGPT.ImageGen', '--prompt', prompt, '--output-dir', output_dir, '--cookie-file', cookie_path]
                proc = subprocess.Popen(command)
                result = proc.communicate()
        for node in all_node_list:
            index = label_to_index[node]
            nodes_list[index]['shape'] = 'image'
            nodes_list[index]['image'] = 'log/' + args.title + '/' + node + '/' + '0' + '.jpeg'
        
    # すでにjsonファイルがある場合は読み込む
    if os.path.exists(log_dir+'graph.json'):
        with open(log_dir+'graph.json', 'r', encoding='utf-8') as f:
            json_dict = json.load(f)
        return json_dict
    
    # extract node information
    node_information_dict = create_node_dict_from_file(log_dir + 'node_info.txt')
    for node_label, node_info in node_information_dict.items():
        node_id = label_to_index[node_label]
        nodes_list[node_id]['title'] = node_info
        
    # extract node groups
    node_group_dict = create_node_dict_from_file(log_dir + 'node_group.txt')
    for node_label, node_group in node_group_dict.items():
        node_id = label_to_index[node_label]
        nodes_list[node_id]['group'] = node_group
        
    # extract node importance
    node_importance_dict = create_node_dict_from_file(log_dir + 'node_importance.txt')
    for node_label, node_importance in node_importance_dict.items():
        node_id = label_to_index[node_label]
        nodes_list[node_id]['size'] = int(MIN_SIZE + float(node_importance) * SIZE_RANGE)
        
    json_dict['nodes'] = nodes_list
    
    
    json_dict, label_to_index = add_edge_to_json_dict(json_dict, log_dir + 'edge.txt', label_to_index)
    json_file = open(log_dir+'graph.json', 'w', encoding='utf-8')
    json.dump(json_dict, json_file, ensure_ascii=False)
    json_file.close()
        
    return json_dict
    

def extract_nodes_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    pattern = r'(?<=- ).+'
    nodes = re.findall(pattern, text)
    return nodes

def create_node_dict_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    lines = text.strip().split('\n')
    result = {}
    for line in lines:
        if ':' in line:
            key, value = line.split(':')
            key = key.replace('-', '').strip()
            result[key] = value.strip()
    return result

def add_edge_to_json_dict(json_dict, file_path, label_to_index):
    if 'edges' not in json_dict:
        json_dict['edges'] = []
        
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    lines = text.strip().split('\n')
    i = 0
    for line in lines:
        if '-' in line and line.count(',') == 2:
            source, relationship, target = line.split(',')
            source = source.replace('-', '').strip()
            target = target.strip()
            if not source in label_to_index.keys():
                label_to_index[source] = len(label_to_index)
                json_dict['nodes'].append({'id': 'node' + str(i), 'label': source, 'size': MIN_SIZE, 'group': 'other'})
                continue
            if not target in label_to_index.keys():
                label_to_index[target] = len(label_to_index)
                json_dict['nodes'].append({'id': 'node' + str(i), 'label': target, 'size': MIN_SIZE, 'group': 'other'})
            json_dict['edges'].append({'id':'edge' + str(i), 'from': 'node'+str(label_to_index[source]), 'label': relationship.strip(), 'to': 'node'+str(label_to_index[target]), 'arrows': 'to'})
            i += 1
    return json_dict, label_to_index
            
def check_files(directory,extension):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(extension):
                return True
    return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--title', type=str, default='浦島太郎')
    parser.add_argument('--show_image', action='store_true')
    args = parser.parse_args()
    
    if not os.path.exists(f'log/{args.title}'):
        print('Downloading...')
        chatbot = ChatbotPrompter(title=args.title)
        asyncio.run(chatbot.main())
        print('Download finished')
    
    json_dict = return_json_dict(args)
    print(json_dict)
    
    return json_dict
    
if __name__ == '__main__':
    main()