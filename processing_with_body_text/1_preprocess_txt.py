import re
import os
import nltk
import argparse
import urllib.request


# gutenbergの作品タイトルを指定すると.txtファイルのurlを返す関数
# TODO: 他の書籍にも対応 (現時点では三匹の子豚のみに対応)
def get_url(title):
    if title=="The Story of the Three Little Pigs":
        url = "https://www.gutenberg.org/ebooks/18155.txt.utf-8"
    
    return url


# gutenbergの.txtファイルのurlを指定すると, txtを返す関数
def get_txt(url):
    with urllib.request.urlopen(url) as u:
        txt = u.read().decode("utf-8")

    return txt


# txtを入力すると, 前処理しbodyを返す関数
# TODO: 他の書籍にも対応 (現時点では三匹の子豚のみに対応)
def preprocess_txt(txt):
    # titleの前処理
    title = re.findall(r"Title: (.+)\r", txt)[0]

    # bodyの前処理
    body = re.findall(r"\*\*\*.+?\*\*\*(.+?)\*\*\*.+?\*\*\*", txt, flags=re.DOTALL)[0]    
    body = re.findall(f"{title.upper()}\.(.+?)\*     \*     \*     \*     \*     \*", body, flags=re.DOTALL)[0]

    # 特殊文字等削除
    body = body.replace("[Illustration]", "")
    body = re.sub("\s+", " ", body).strip()
    
    # 単語の前後の _ を削除
    word_list = []
    for word in body.split():
        if word[0] == "_":
            word = word[1:]
        if word[-1] == "_":
            word = word[:-1]
        word_list.append(word)
    body = " ".join(word_list)

    # # log/{title}/clean_body.txt に保存 (必要ならコメントアウト)
    # os.makedirs(f"log/{title}", exist_ok=True)
    # with open(f"log/{title}/clean_body.txt", "w", encoding="utf-8") as f:
    #     f.write(body)
    
    return body


# bodyを文ごとに区切り保存する関数
def save_splited_body_by_sentence(body, title):
    body_sentences = nltk.sent_tokenize(body)

    # log/{title}/body.txt に保存
    # 各行にsentence_id(何番目の文かを表すid)と文を保存
    os.makedirs(f"log/{title}", exist_ok=True)
    with open(f"log/{title}/body.txt", "w", encoding="utf-8") as f:
        for sentence_idx, body_sentence in enumerate(body_sentences):
            f.write(f"{sentence_idx}\t{body_sentence}\n")


# titleを入力すると, body.txtを1900文字単位で区切り, 区切った文章を保存する関数
# 1900について: EdgeGPTへの入力は"指示+2つの文章" → この長さがEdgeGPTの入力制限4000文字以下になるように制御
def savesplited_body_by_len(title):
    # 文単位に分割された本文を読み込む
    with open(f"log/{title}/body.txt", encoding="utf-8") as f:
        sentences = f.read().split("\n")[:-1]
    
    # 1900文字単位で区切り, log/{title}/body_{sep_idx}.txtに保存していく
    sep_sentences = []
    sep_idx = 0
    total_len = 0
    for sentence in sentences:
        # 改行も1文字とカウントされるため, 文の長さに1を追加
        sentence_len = len(sentence) + 1
        # sep_sentencesの長さが1900文字未満の場合: そのまま追加
        if total_len + sentence_len < 1900:
            sep_sentences.append(sentence)
            total_len += sentence_len
        # sep_sentencesの長さが1900文字以上の場合: これまでのsep_sentencesを保存し, 変数を更新
        else:
            # これまでのsep_sentencesを保存
            with open(f"log/{title}/body_{sep_idx}.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(sep_sentences)+"\n")
            # 変数を更新
            sep_sentences = [sentence]
            sep_idx += 1
            total_len = sentence_len

    # 最後に残っているsep_sentencesを保存
    with open(f"log/{title}/body_{sep_idx}.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(sep_sentences)+"\n")


def main():
    # 入力でtitleを指定
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", type=str, default="The Story of the Three Little Pigs")
    args = parser.parse_args()

    title = args.title

    # すでに実行済みの場合, 実行しない
    if os.path.exists(f"log/{title}/body.txt"):
        print("The preprocessed text already exists!")
        exit()
    

    # titleを基に, gutenbergのtxtファイルのurlを得る
    url = get_url(title)
    # txtファイルのurlを基に, 生のテキストデータを得る
    txt = get_txt(url)
    # 生のテキストデータを基に, bodyを取得する
    body = preprocess_txt(txt)
    # bodyを文ごとに区切り保存する
    save_splited_body_by_sentence(body, title)
    # bodyを短く分割して保存する
    savesplited_body_by_len(title)


if __name__ == "__main__":
    main()
