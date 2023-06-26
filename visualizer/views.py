from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import TemplateView
import json
import re

class Visualizer(TemplateView):
    def __init__(self):
        pass

    def get_data(self, request):
        with open('sample_graph.json',encoding='utf-8') as f: #add encoding='utf-8'
            graph_data = json.load(f)
            
        title = graph_data['title']
        
        summary_list = graph_data['summary']
        chapter_num = request.session.get('chapter_num')
        if chapter_num is None:
            chapter_num = 0
        summary = ""
        if request.method == 'POST':
            if 'event' in request.POST:
                if request.POST['event'] == 'prev' and 0 < chapter_num:
                    chapter_num -= 1
                if request.POST['event'] == 'next' and chapter_num < len(summary_list):
                    chapter_num += 1
                print(f"第{chapter_num}段落")
                request.session['chapter_num'] = chapter_num
        summary = "".join(summary_list[:chapter_num])
        
        nodes = ""
        for node in graph_data['nodes']:
            if 'period' not in node or node['period'] == 'all':
                node.pop('period', None)
            if 'period' in node and chapter_num not in node['period']:
                continue
            line = json.dumps(node, ensure_ascii=False)
            line = re.sub('"([a-z]+)":', r'\1:', line)
            line = line.replace('"', "'")
            nodes += line+",\n"
            
        edges = ""
        for edge in graph_data['edges']:
            if 'period' not in edge or edge['period'] == 'all':
                edge.pop('period', None)
            if 'period' in edge and chapter_num not in edge['period']:
                continue
            line = json.dumps(edge, ensure_ascii=False)
            line = re.sub('"([a-z]+)":', r'\1:', line)
            line = line.replace('"', "'")
            edges += line+",\n"
        
        params = {
            'title': title,
            'summary':summary,
            'nodes': nodes,
            'edges': edges
        }
        
        return params
 
    def get(self, request):    
        params = self.get_data(request)
        return render(request, 'visualizer/index.html', params)
    
    def post(self, request):
        params = self.get_data(request)
        return redirect('index')
        # return render(request, 'visualizer/network.html', params)
