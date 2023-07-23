# 本文を用いた知識グラフ, 要約の作成
## about
- 本文を場面に基づき分割し, 各場面の知識グラフ及び要約を作成 (宮野担当分)
- 7/22: 本文を場面を基に分割するコードを追加 (1.~3.)
- 7/23: 本文の各場面を要約するコードを追加 (4.)

## requirements
- (django==4.2.2)
- EdgeGPT==0.11.5
- **nltk==3.8.1**
- **pandas==2.0.3**

## 事前準備
- 以下の手順を参考にbing_cookies_.jsonを用意
    - https://github.com/acheong08/EdgeGPT
- nltk.punktのダウンロード
    ```
    import nltk
    nltk.download('punkt')
    ```

## 実行方法
- python 1_preprocess_txt.py --title "title"
    - 本文をダウンロードし, 前処理を行い, データを短い文章に分割する
- python 2_group_sentence_by_scene.py --title "title" --scene_type "location" --is_show_log False
    - 前処理済みの本文を, scene_type(location or time or character)に基づき分類する
    - 三匹の子豚において...
        - location: 分割自体は良さそう, 名前もだいたいOK
        - time: 分割自体は良さそう, 分割の名前が良くない
        - character: 登場人物が少ないので, ほとんど分割されない
- python 3_split_body_by_scene.py --title "title" --use_location True --use_time False --use_character False
    - 分類済みの本文を, 分類に基づき分割する
- python 4_summarize_splited_body.py --title "title" --use_location True --use_time False --use_character False --is_show_log False
    - 分割済みの本文を要約する

## 例外処理
- Exception: CaptchaChallenge: User needs to solve CAPTCHA to continue.
    - このエラーが発生した場合, Bing AIにアクセスして認証を通す必要がある
