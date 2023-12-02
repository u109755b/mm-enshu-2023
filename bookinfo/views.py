from django.shortcuts import render
import json

def index(request):
    with open('bookinfo/static/bookinfo/work_info.json', encoding='utf-8') as f:
        work_info = json.load(f)
    params = {
        'json_data': json.dumps(work_info)
    }
    return render(request, 'bookinfo/index.html', params)