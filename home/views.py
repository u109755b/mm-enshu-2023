from django.shortcuts import render
import os
import glob
import requests

def index(request):
    # フォルダ・ファイル名指定
    summarized_data_dir = 'visualizer/static/visualizer/summarized_data'
    cover_image_dir = 'home/static/home/cover_image'
    title_file_name = 'title.txt'
    cover_image_name = 'cover_image.jpg'

    # 要約データが存在する物語のgutenbergIDのリストを作成する
    gutenbergIDs = []
    story_data_folders = glob.glob(f'{summarized_data_dir}/*')
    for story_data_folder in story_data_folders:
        gutenbergID = story_data_folder.split('/')[-1]
        if not gutenbergID.isdecimal(): continue
        gutenbergIDs.append(gutenbergID)
    gutenbergIDs.sort()

    # 物語のタイトルと表紙画像を保存する
    titles = []
    for gutenbergID in gutenbergIDs:
        visualizer_book_dir = f'{summarized_data_dir}/{gutenbergID}'
        home_book_dir = f'{cover_image_dir}/{gutenbergID}'
        os.makedirs(home_book_dir, exist_ok=True)

        # タイトル
        with open(f'{visualizer_book_dir}/{title_file_name}', encoding='utf-8') as f:
            title = f.read()
        with open(f'{home_book_dir}/{title_file_name}', 'w', encoding='utf-8') as f:
            f.write(title)
        titles.append(title)

        # 表紙画像
        if not f'{home_book_dir}/{cover_image_name}' in glob.glob(f'{home_book_dir}/*'):
            if gutenbergID == '0': gutenbergID = '18155'    # サンプルの三匹の子豚
            cover_image_url = f'https://www.gutenberg.org/cache/epub/{gutenbergID}/pg{gutenbergID}.cover.medium.jpg'
            # continue
            print(f'"{title}" の表紙画像をダウンロードしています...')
            print(f'url: {cover_image_url}')
            response  = requests.get(cover_image_url)
            cover_image = response.content
            with open(f'{home_book_dir}/{cover_image_name}', 'wb') as f:
                f.write(cover_image)
            print(f'"{title}" の表紙画像を {home_book_dir}/{cover_image_name} に保存しました')

    params = {'gutenbergIDs': gutenbergIDs, "titles": titles}
    return render(request, 'home/index2.html', params)