from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.generic import TemplateView
import json
import re

class ViewManager:
    # 初期化（requestデータと要約データを読み込む）
    def __init__(self, request):
        with open('visualizer/static/visualizer/summarized_data/0/all_data.json', encoding='utf-8') as f:
            self.section_data = json.load(f)
        self.chapter_id_list = self._create_chapter_id_list(self.section_data)
        self.request = request
        self.chapter_id = self.request.session.get('chapter_id')

    def _create_chapter_id_list(self, section_data, depth=0, parent_id=[]):
        chapter_id_list = []
        for i, section in enumerate(section_data):
            num = i+1
            parent_id.append(str(num))
            if 'subSection' not in section:
                chapter_id_list.append('-'.join(parent_id))
            else:
                sub_chapter_id_list = self._create_chapter_id_list(section['subSection'], depth+1, parent_id)
                chapter_id_list.extend(sub_chapter_id_list)
            parent_id.pop()
        return chapter_id_list

    def _create_tab_list(self, section_data, depth=0, parent_id=[]):
        tab_list = []
        for i, section in enumerate(section_data):
            num = i+1
            parent_id.append(str(num))

            tab = {'class': ['tab']}
            if 0 < depth:
                tab['class'].append('sub{}-tab'.format(depth if 1<depth else ''))
            tab['id'] = '-'.join(parent_id)
            tab['sectionName'] = section['sectionName']
            tab_list.append(tab)

            if 'subSection' in section:
                group = {'class': ['group']}
                group['subSection'] = self._create_tab_list(section['subSection'], depth+1, parent_id)
                tab_list.append(group)

            parent_id.pop()
        return tab_list

    def _create_tab_div(self, tab_list, depth=3):
        tab_div = []
        for obj in tab_list:
            if 'tab' in obj['class']:
                tab = obj
                class_str = ' '.join(tab['class'])
                id = tab['id']
                section_name = tab['sectionName']
                tab_div.append('<div class="{}" id="{}">{}</div>'.format(class_str, id, section_name))
            if 'group' in obj['class']:
                group = obj
                tab_div.append('<div class="group">')
                tab_div.append(self._create_tab_div(group['subSection'], depth+1))
                tab_div.append('</div>')
        return '\n{}'.format('\t'*depth).join(tab_div)

    # タブのhtmlコードを階層的に作成する
    def create_tab_div(self):
        tab_list = self._create_tab_list(self.section_data)
        tab_div = self._create_tab_div(tab_list)
        return tab_div

    # 各章の要約データを作成する
    def get_chapter_data(self, chapter_id=None):
        if chapter_id: self.chapter_id = chapter_id
        if not self.chapter_id:
            return {'chapter_id': None, 'summary': '', 'nodes': [], 'edges': []}
        section_data = self.section_data
        for num in self.chapter_id.split('-'):
            section_data = section_data[int(num)-1]
            if 'subSection' in section_data:
                section_data = section_data['subSection']
        chapter_data = section_data
        if 'summary' not in chapter_data: chapter_data['summary'] = ''
        if 'nodes' not in chapter_data: chapter_data['nodes'] = []
        if 'edges' not in chapter_data: chapter_data['edges'] = []
        chapter_data['chapter_id'] = self.chapter_id
        self.request.session['chapter_id'] = self.chapter_id
        return chapter_data

    # 章を1つ進める
    def forward_chapter(self):
        if not self.chapter_id: index = -1
        else: index = self.chapter_id_list.index(self.chapter_id)
        if index + 1 < len(self.chapter_id_list):
            index += 1
        self.chapter_id = self.chapter_id_list[index]
        self.request.session['chapter_id'] = self.chapter_id
        return self.chapter_id

    # 章を1つ戻す
    def back_chapter(self):
        if not self.chapter_id: return None
        index = self.chapter_id_list.index(self.chapter_id)
        if 0 <= index - 1:
            index -= 1
        self.chapter_id = self.chapter_id_list[index]
        self.request.session['chapter_id'] = self.chapter_id
        return self.chapter_id


# 最初のページ読み込みや再読み込み時の処理
def index(request):
    request.session.clear()
    view_manager = ViewManager(request)
    tab_div = view_manager.create_tab_div()
    chapter_data = view_manager.get_chapter_data()
    params = {
        'tab_div': tab_div,
        'title': '三匹の子豚',
        'summary': chapter_data['summary'],
        'nodes': json.dumps(chapter_data['nodes'], ensure_ascii=False),
        'edges': json.dumps(chapter_data['edges'], ensure_ascii=False),
    }
    return render(request, 'visualizer/index.html', params)

# 初期化時の処理
def init(request):
    chapter_id = request.session.get('chapter_id')
    return JsonResponse({'chapter_id': chapter_id})

# タブが押されたときの処理
def select_section(request):
    chapter_id = request.GET.get('chapter_id', None)
    view_manager = ViewManager(request)
    if chapter_id in view_manager.chapter_id_list:
        chapter_data = view_manager.get_chapter_data(chapter_id)
    else:
        chapter_data = {}
    return JsonResponse(chapter_data)

# 「前へ」ボタンが押された時の処理
def prev_paragraph(request):
    view_manager = ViewManager(request)
    view_manager.back_chapter()
    chapter_data = view_manager.get_chapter_data()
    return JsonResponse(chapter_data)

# 「次へ」ボタンが押された時の処理
def next_paragraph(request):
    view_manager = ViewManager(request)
    view_manager.forward_chapter()
    chapter_data = view_manager.get_chapter_data()
    return JsonResponse(chapter_data)