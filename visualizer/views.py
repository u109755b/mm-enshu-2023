from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.generic import TemplateView
import json
from mm_enshu_2023 import utils

class ViewManager:
    # 初期化
    def __init__(self, request, gutenbergID=0, sample_id=None):
        self.request = request
        self.gutenbergID = gutenbergID

        self.title = utils.get_title(gutenbergID)

        self.sample_id_list = utils.get_sample_id_list(gutenbergID)
        self.sample_id = self.request.session.get('sample_id')
        if sample_id: self.sample_id = sample_id
        if self.sample_id not in self.sample_id_list:
            self.sample_id = self.sample_id_list[0]

        self.section_data = utils.get_section_data(gutenbergID, self.sample_id)

        self.chapter_id_list = utils.get_chapter_id_list(gutenbergID, self.sample_id)
        self.chapter_id = self.request.session.get('chapter_id')
        if self.chapter_id not in self.chapter_id_list:
            self.chapter_id = self.chapter_id_list[0]

    # section_dataから、tabのhtmlを作るための構造データtab_listを作成する（class内からのみ呼び出される）
    def _create_tab_list(self, section_data, depth=0, parent_id=[]):
        tab_list = []
        for i, section in enumerate(section_data):
            num = i+1
            parent_id.append(str(num))

            tab = {'class': ['tab']}
            if 'subSection' in section:
                tab['class'].append('expand-icon')
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

    # tab_listから、tabのhtmlであるtab_htmlを作成する（class内からのみ呼び出される）
    def _create_tab_html(self, tab_list, depth=3):
        tab_html = []
        for obj in tab_list:
            if 'tab' in obj['class']:
                tab = obj
                class_str = ' '.join(tab['class'])
                id = tab['id']
                section_name = tab['sectionName']
                tab_html.append('<div class="{}" id="{}">{}</div>'.format(class_str, id, section_name))
            if 'group' in obj['class']:
                group = obj
                tab_html.append('<div class="group">')
                tab_html.append(self._create_tab_html(group['subSection'], depth+1))
                tab_html.append('</div>')
        return '\n{}'.format('\t'*depth).join(tab_html)

    # タブのhtmlコードを階層的に作成する
    def create_tab_html(self):
        tab_list = self._create_tab_list(self.section_data)
        tab_html = self._create_tab_html(tab_list)
        return tab_html

    # サンプルを選択するオプションのhtmlコードを作成する
    def create_option_html(self):
        option_html = ''
        for sample_id in self.sample_id_list:
            option_html += f'<option value="{sample_id}">{sample_id}</option>'
        return option_html

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
        chapter_data['summary'] = '<p><b>{}</b><br>{}</p>'.format(section_data['sectionName'], chapter_data['summary'])
        chapter_data['chapter_id'] = self.chapter_id
        return chapter_data

    # 章を1つ進める
    def forward_chapter(self):
        if not self.chapter_id: index = -1
        else: index = self.chapter_id_list.index(self.chapter_id)
        if index + 1 < len(self.chapter_id_list):
            index += 1
        self.chapter_id = self.chapter_id_list[index]
        return self.chapter_id

    # 章を1つ戻す
    def back_chapter(self):
        if not self.chapter_id: return None
        index = self.chapter_id_list.index(self.chapter_id)
        if 0 <= index - 1:
            index -= 1
        self.chapter_id = self.chapter_id_list[index]
        return self.chapter_id

    # セッションデータ保存
    def save_session_data(self):
        self.request.session['sample_id'] = self.sample_id
        self.request.session['chapter_id'] = self.chapter_id
        self.request.session.save()



# 最初のページ読み込みや再読み込み時の処理
def index(request, gutenbergID=0):
    for key in list(request.session.keys()):
        del request.session[key]
    request.session.clear()
    view_manager = ViewManager(request, gutenbergID)
    tab_html = view_manager.create_tab_html()
    option_html = view_manager.create_option_html()
    chapter_data = view_manager.get_chapter_data()
    params = {
        'gutenbergID': str(gutenbergID),
        'title': view_manager.title,
        'tabHTML': tab_html,
        'optionHTML': option_html,
        'summary': chapter_data['summary'],
        'nodes': json.dumps(chapter_data['nodes'], ensure_ascii=False),
        'edges': json.dumps(chapter_data['edges'], ensure_ascii=False),
    }
    view_manager.save_session_data()
    return render(request, 'visualizer/index.html', params)

# 初期化時の処理
def init(request, gutenbergID=0):
    chapter_id = request.session.get('chapter_id')
    return JsonResponse({'chapter_id': chapter_id})

# タブが押されたときの処理
def select_chapter(request, gutenbergID=0):
    chapter_id = request.GET.get('chapter_id', None)
    view_manager = ViewManager(request, gutenbergID)
    if chapter_id in view_manager.chapter_id_list:
        chapter_data = view_manager.get_chapter_data(chapter_id)
    else:
        chapter_data = {}
    view_manager.save_session_data()
    return JsonResponse(chapter_data)

# 「前へ」ボタンが押された時の処理
def prev_chapter(request, gutenbergID=0):
    view_manager = ViewManager(request, gutenbergID)
    view_manager.back_chapter()
    chapter_data = view_manager.get_chapter_data()
    view_manager.save_session_data()
    return JsonResponse(chapter_data)

# 「次へ」ボタンが押された時の処理
def next_chapter(request, gutenbergID=0):
    view_manager = ViewManager(request, gutenbergID)
    view_manager.forward_chapter()
    chapter_data = view_manager.get_chapter_data()
    view_manager.save_session_data()
    return JsonResponse(chapter_data)

# sample選択ボタンが押された時の処理
def select_sample(request, gutenbergID=0):
    sample_id = request.GET.get('sample_id', None)
    view_manager = ViewManager(request, gutenbergID, sample_id)
    chapter_data = view_manager.get_chapter_data()
    view_manager.save_session_data()
    return JsonResponse(chapter_data)