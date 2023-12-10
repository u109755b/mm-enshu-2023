from django.shortcuts import render
import os
import requests
from mm_enshu_2023 import utils

def index(request):
    # フォルダ・ファイル名指定
    cover_image_dir = 'home/static/home/cover_image'
    title_file_name = 'title.txt'
    cover_image_name = 'cover_image.jpg'

    gutenbergIDs = utils.get_gutenbergIDs()
    titles = []

    # 物語のタイトルと表紙画像を保存する
    for gutenbergID in gutenbergIDs:
        home_book_dir = f'{cover_image_dir}/{gutenbergID}'

        # タイトル
        title = utils.get_title(gutenbergID)
        utils.save_txt(f'{home_book_dir}/{title_file_name}', title)
        titles.append(title)

        # 表紙画像
        if not os.path.exists(f'{home_book_dir}/{cover_image_name}'):
            if gutenbergID == '0': gutenbergID = '18155'    # サンプルの三匹の子豚
            cover_image_url = f'https://www.gutenberg.org/cache/epub/{gutenbergID}/pg{gutenbergID}.cover.medium.jpg'
            print(f'"{title}" の表紙画像をダウンロードしています...')
            print(f'url: {cover_image_url}')
            response  = requests.get(cover_image_url)
            cover_image = response.content
            utils.save_image(f'{home_book_dir}/{cover_image_name}', cover_image)
            print(f'"{title}" の表紙画像を {home_book_dir}/{cover_image_name} に保存しました')

    params = {'gutenbergIDs': gutenbergIDs, "titles": titles}
    return render(request, 'home/index2.html', params)