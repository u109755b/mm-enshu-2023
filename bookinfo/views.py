from django.shortcuts import render
from bookinfo.get_work_info import main as get_work_info
from mm_enshu_2023 import utils
import json
import os

def index(request, gutenbergID=0):
    # title = utils.get_title(gutenbergID)
    
    titile_ls = {"120": "Treasure Island", "11": "Alice's Adventures in Wonderland", "1661": "The Adventures of Sherlock Holmes", "18155": "The Three Little Pigs", "0": "The Three Little Pigs", "829": "Gulliver's Travels"}
    title = titile_ls[f"{gutenbergID}"]
    
    folder_path = "bookinfo/static/json"
    file_path = os.path.join(folder_path, f"{title}.json")

    if not os.path.exists(file_path):
        get_work_info(title)
    with open(file_path, encoding='utf-8') as f:
        work_info = json.load(f)
    params = {
        'json_data': json.dumps(work_info),
        'gutenbergID': gutenbergID
    }
    return render(request, 'bookinfo/index.html', params)