# 本文に基づく知識グラフ構築 (ChatGPT ver)
### 対象物語 (随時追加予定)
| gutenbergID | name | #words |
| ---- | ---- | ---- |
| 18155 | The Story of the Three Little Pigs | 960 |
| 1661 | The Adventures of Sherlock Holmes\* | 8,520 |
| 11 |  Alice's Adventures in Wonderland by Lewis Carroll | 26,520 |
| 120 | TREASURE ISLAND | 67,870 |
| 829 | GULLIVER'S TRAVELS INTO SEVERAL REMOTE NATIONS OF THE WORLD | 105,080 |
\*  1_preprocess_txt.py 実行後人手で I. A Scandal in Bohemia のみを抽出


### 更新履歴
- 20231125: 1_preprocess_txt.py 取り敢えず完成
- 20231126: 2_summarization.py 取り敢えず完成
- 20231127: 3_create_knowledge_graph.py 取り敢えず完成 (プロンプト改善が必要)


### コードの説明
- 1_preprocess_txt.py: storyID (gutenbergID) を入力すると, 本文を場面ごとに分割し保存する.
- 2_summarization.py: storyID を入力すると, 各場面の本文の要約を行う.
- 3_create_knowledge_graph: storyID を入力すると, 各場面の node, edge を取得する.
- 3_create_knowledge_graph_one_scene: storyID, sceneID を入力すると, 指定した場面の node, edge を取得する.
- 4_create_json.py: storyID を入力すると, graph.json を作成する.
- create_json.sh: storyID を入力すると, 1~4 をまとめて実行する


### 出力例 (3回実行し, 各結果を sample0, 1, 2 に追加)
- 20231127: 18155 ChatGPT-output 追加
- 20231201: 11 ChatGPT-output 追加
- 20231201: 1661 ChatGPT-output 追加
- 20231201: 120 ChatGPT-output 追加 (sample0のみ)


### コスト概算
- 18155: The Story of the Three Little Pigs (960)
    | program | time | money (I/O, $) |
    | ---- | ---- | ---- |
    | 1_preprocess_txt.py | 0:01 | --- |
    | 2_summarization.py | 0:10 | 0.01/0.01 |
    | 3_create_knowledge_graph.py | 2:30 | 0.03/0.06 |
    | 4_create_json.py | ?:?? | --- |


- 1661: The Adventures of Sherlock Holmes (8,520)
    | program | time | money (I/O, $) |
    | ---- | ---- | ---- |
    | 1_preprocess_txt.py | 0:01 | --- |
    | 2_summarization.py | 0:30 | 0.10/0.01 |
    | 3_create_knowledge_graph.py | 4:00 | 0.25/0.15 |
    | 4_create_json.py | ?:?? | --- |


- 11: Alice's Adventures in Wonderland by Lewis Carroll (26,520)
    | program | time | money (I/O, $) |
    | ---- | ---- | ---- |
    | 1_preprocess_txt.py | 0:01 | --- |
    | 2_summarization.py | 1:00 | 0.30/0.05 |
    | 3_create_knowledge_graph.py | 19:30 | 0.75/0.60 |
    | 4_create_json.py | ?:?? | --- |


- 120: TREASURE ISLAND (67,870)
    | program | time | money (I/O, $) |
    | ---- | ---- | ---- |
    | 1_preprocess_txt.py | 0:01 | --- |
    | 2_summarization.py | 3:30 | 0.70/0.15 |
    | 3_create_knowledge_graph.py | 70:30 | 1.90/1.50 |
    | 4_create_json.py | ?:?? | --- |


- 829: GULLIVER'S TRAVELS INTO SEVERAL REMOTE NATIONS OF THE WORLD (105,080)
    | program | time | money (I/O, $) |
    | ---- | ---- | ---- |
    | 1_preprocess_txt.py | 0:01 | --- |
    | 2_summarization.py | ?:?? | ??? |
    | 3_create_knowledge_graph.py | ?:?? | ??? |
    | 4_create_json.py | ?:?? | --- |


### requirements
- ChatGPT API の利用準備