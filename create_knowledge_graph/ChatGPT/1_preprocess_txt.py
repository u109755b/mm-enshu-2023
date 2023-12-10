# storyID を入力すると (1)本文全体，(2)場面ごとに分割された本文をファイルに保存する
# (1): log/{storyID}/body.txt
# (2): log/{storyID}/body_scene{sceneID}.txt
# 20231125 取り敢えず完成 (11,120,829,1661,18155 に対応)
# TODO: 他の物語にも対応しているか確認 (対応が難しい物語は演習の対象から除いてもよさそう)

import re
import os
import argparse
import urllib.request


# 本文を入力すると目次を取得し, 目次のリストと目次を除いた本文を返す関数
# 目次は最初が contents で, 目次の間は文頭が空白であることを利用
def get_contents(body):
    contents_flg = 0    # 目次の間はこのフラグが1になる
    body_flg = 0        # 目次後の本文ではこのフラグが1になる
    contents_list = []  # 目次を格納
    cleaned_body = ""
    for line in body.split("\n"):
        if re.match(r"\s*contents", line, flags=re.IGNORECASE):
            contents_flg = 1
            continue
            
        if contents_flg:
            if line[0] == " ":  # 文頭が空白の場合目次が続いていると判断
                contents_list.append(line.strip())
            else:
                body_flg = 1
                contents_flg = 0
        
        if body_flg:
            cleaned_body += line+"\n"
    
    return contents_list, cleaned_body.strip()


# storyID を入力すると本文を前処理してファイルに保存する
# また, 本文を場面ごとに分割して分割後の本文をファイルに保存する
def preprocess_txt(storyID):
    # 生のテキストを取得
    storyURL = f"https://www.gutenberg.org/cache/epub/{storyID}/pg{storyID}.txt.utf8"
    with urllib.request.urlopen(storyURL) as u:
        txt = u.read().decode("utf-8")

    # body, title の抽出
    body = re.findall(r"\*\*\*.+?\*\*\*(.+?)\*\*\*.+?\*\*\*", txt, flags=re.DOTALL)[0]
    title = re.findall(r"Title: (.+?)\r\n", txt, flags=re.DOTALL)[0]

    # 特殊文字等を削除
    body = body.replace("[Illustration]", "")
    body = body.split("FOOTNOTES:")[0]

    body = re.sub(r"(\S+)\r\n(\S+)", r"\1 \2", body)
    body = re.sub(r"(\r\n)+", r"\n", body)

    body = re.sub(r"(\s+)_(\S+)", r"\1\2", body)
    body = re.sub(r"(\S+)_(\s+)", r"\1\2", body)

    body = body.strip()
    
    # 前後の注釈を削除し本文のみを抽出
    # 三匹の子豚の場合は特殊な処理が必要
    if storyID == 18155:
        body = re.findall(f"{title}\.(.+?)\*     \*     \*     \*     \*     \*", body, flags=re.IGNORECASE|re.DOTALL)[0].strip()
        contents_list = []
    # 三匹の子豚以外では, 目次後が本文 (目次抽出関数を利用)
    else:
        contents_list, body = get_contents(body)

    # 本文を log/{storyID}/body.txt に保存
    os.makedirs(f"log/{storyID}", exist_ok=True)
    with open(f"log/{storyID}/body.txt", "w", encoding="utf-8") as f:
        f.write(body)
    

    # 本文の分割を行う
    # 数字のパターンを定義 (ローマ数字+".", アラビア数字, 数字を表す英単語)
    roman_numerals = "(?=[LXVI])(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})\."     # 行の先頭が.である場合を除外
    arabic_numerals = "(?<![\d\s])\d{1,2}(?!\d)"                        # 行の先頭に空白がある場合を除外, 数字を2桁以下に限定
    words_for_numbers = "(ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN)"

    # 分割するタイトル行のパターンを定義
    split_pattern = re.compile(
        fr"^(CHAPTER|PART)?\s*({roman_numerals}|{arabic_numerals}|{words_for_numbers})", re.MULTILINE
    )

    split_bodys = []    # 場面分割後の文章のリスト
    split_body = ""     # 場面分割後の文章
    lines = body.split("\n")    # 本文の各行を格納
    line_id = 0                 # 本文の何行目を処理しているか表す変数
    while line_id < len(lines):
        line = lines[line_id]
        # タイトルのみの行は分割後の本文に含めない
        if re.match(title, line, flags=re.IGNORECASE):
            line_id += 1
            continue

        # 行が分割パターン (タイトル行, 目次と同じ行) に該当する場合, split_body をリストに格納し初期化する
        if re.search(split_pattern, line) or line in contents_list:
            split_bodys.append(split_body.strip()) if split_body else None
            next_line = lines[line_id+1]
            # 次の行も分割パターンに該当する場合, 2行をまとめて処理する
            if re.search(split_pattern, next_line) or next_line in contents_list:
                split_body = line + "\n" + next_line + "\n"
                line_id += 2
                continue
            else:
                split_body = line + "\n"
                line_id += 1
                continue
        # 行が分割パターンに該当しない場合, この行を split_body に追加
        else:
            split_body += line + "\n"
            line_id += 1

    split_bodys.append(split_body.strip())

    for sceneID, split_body in enumerate(split_bodys):
        with open(f"log/{storyID}/body_scene{sceneID}.txt", "w", encoding="utf-8") as f:
            f.write(split_body)
    

def main():
    # 入力で storyID を指定
    parser = argparse.ArgumentParser()
    parser.add_argument("--storyID", type=int)
    args = parser.parse_args()

    storyID = args.storyID

    # すでに実行済みの場合, 実行しない
    if os.path.exists(f"log/{storyID}/body_scene0.txt"):
        print("The preprocessed text already exists!")
        exit()


    # storyID を基に (1)本文全体，(2)場面ごとに分割された本文をファイルに保存する
    preprocess_txt(storyID)


if __name__ == "__main__":
    main()
