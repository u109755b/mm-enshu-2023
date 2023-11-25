# 本文に基づく知識グラフ構築 (ChatGPT ver)
- 以下の物語に対応予定
    | gutenbergID | name | #words |
    | ---- | ---- | ---- |
    | 18155 | The Story of the Three Little Pigs | 960 |
    | 1661 | The Adventures of Sherlock Holmes (I. A Scandal in Bohemia) | 8,520 |
    | 11 |  Alice's Adventures in Wonderland by Lewis Carroll | 26,520 |
    | 120 | TREASURE ISLAND | 67,870 |
    | 829 | GULLIVER'S TRAVELS INTO SEVERAL REMOTE NATIONS OF THE WORLD | 105,080 |

- 更新履歴
    - 20231125: 1_preprocess_txt.py 取り敢えず完成

- コードの説明
    - 1_preprocess_txt.py: storyID (gutenbergID) を入力すると, 本文を場面ごとに分割し保存する.
    - 2_summarization.py: storyID を入力すると, 各場面の本文の要約を行う.
    - 3_create_knowledge_graph: storyID を入力すると, 各場面の node, edge を取得する.
    - 4_create_json.py: storyID を入力すると, graph.json を作成する.
    - create_json.sh: storyID を入力すると, 1~4 をまとめて実行する

- requirements
    - ChatGPT API の利用準備