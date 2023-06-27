import urllib.request
import re

# gutenbergの.txtファイルのurlを指定すると, txtを返す関数
def get_txt(url):
    '''
    gutenbergの.txtファイルのurlを指定すると, txtを返す関数
    '''
    # todo: 書籍タイトルを指定することで動作するように拡張
    with urllib.request.urlopen(url) as u:
        txt = u.read().decode("utf-8")
        # 保存する必要がある場合は, ここのコメントアウトを解除
        # with open(url.split("/")[-1], "w", encoding="utf-8") as o:
        #     o.write(txt)

    return txt

# txtを入力すると, title, bodyを返す関数
def preprocess_txt(txt):
    '''
    txtを入力すると, title, bodyを返す関数
    現状, 3匹の子豚にしか対応していない
    '''
    # todo: 他の書籍にも対応
    # titleの前処理
    title = re.findall(r"Title: (.+)\r", txt)[0]

    # bodyの前処理
    body = re.findall(r"\*\*\*.+?\*\*\*(.+?)\*\*\*.+?\*\*\*", txt, flags=re.DOTALL)[0]    
    body = re.findall(f"{title.upper()}\.(.+?)\*     \*     \*     \*     \*     \*", body, flags=re.DOTALL)[0]

    # 特殊文字等削除
    body = body.replace("[Illustration]", "")
    body = re.sub("\s+", " ", body).strip()

    # {title}.body.txt に保存: 必要ならコメントアウト解除
    # with open(f"{title}.txt", "w", encoding="utf-8") as f:
    #     f.write(body)

    return title, body

# todo: 代名詞の処理
# todo: 文章が長い場合の処理

if __name__ == "__main__":
    # 3匹の子豚の場合の実行例
    url = "https://www.gutenberg.org/ebooks/18155.txt.utf-8"
    txt = get_txt(url)

    title, body = preprocess_txt(txt)
    print(body) # body の確認
