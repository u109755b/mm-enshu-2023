from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.generic import TemplateView
import json
import re


# 物語データを取得する
def get_story_data(request, prev_next='keep'):
    # 物語データ読み込み
    with open('story_data/sample_json/sample_graph_ver1.json', encoding='utf-8') as f:
        graph_data = json.load(f)

    # 章番号計算
    chapter_num = request.session.get('chapter_num')
    if chapter_num is None:
        chapter_num = 0
    if prev_next == 'prev' and 0 < chapter_num:
        chapter_num -= 1
    if prev_next == 'next' and chapter_num < len(graph_data['summary']):
        chapter_num += 1
    print(f"第{chapter_num}段落")
    request.session['chapter_num'] = chapter_num
    request.session.save()

    # タイトル取得
    title = graph_data['title']

    # 要約取得
    summary = "".join(graph_data['summary'][:chapter_num])

    # ノード情報取得
    nodes = []
    for node in graph_data['nodes']:
        if 'period' not in node or node['period'] == 'all':
            node.pop('period', None)
        if 'period' in node and chapter_num not in node['period']:
            continue
        nodes.append(node)

    # エッジ情報取得
    edges = []
    for edge in graph_data['edges']:
        if 'period' not in edge or edge['period'] == 'all':
            edge.pop('period', None)
        if 'period' in edge and chapter_num not in edge['period']:
            continue
        edges.append(edge)

    # 情報をまとめる
    params = {
        'title': title,
        'summary':summary,
        'nodes': nodes,
        'edges': edges
    }

    return params


# 最初のページ読み込みや再読み込み時の処理
def index(request):
    params = get_story_data(request)
    params['nodes'] = json.dumps(params['nodes'], ensure_ascii=False)
    params['edges'] = json.dumps(params['edges'], ensure_ascii=False)
    return render(request, 'visualizer/old_indexes/index_ver1.html', params)

# 「前へ」ボタンが押された時の処理
def prev_paragraph(request):
    params = get_story_data(request, prev_next='prev')
    return JsonResponse(params)

# 「次へ」ボタンが押された時の処理
def next_paragraph(request):
    params = get_story_data(request, prev_next='next')
    return JsonResponse(params)