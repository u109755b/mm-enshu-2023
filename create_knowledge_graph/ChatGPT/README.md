# 本文に基づく知識グラフ構築 (ChatGPT ver)
### 対象物語 (随時追加予定)
| num | gutenbergID | name | #words | condition |
| ---- | ---- | ---- | ---- | ---- |
| 1 | 18155 | The Story of the Three Little Pigs | 960 | fin |
| 2 | 1661 | The Adventures of Sherlock Holmes\* | 8,520 | fin |
| 3 | 11 |  Alice's Adventures in Wonderland by Lewis Carroll | 26,520 | fin |
| 4 | 120 | TREASURE ISLAND | 67,870 | fin |
| 5 | 829 | GULLIVER'S TRAVELS INTO SEVERAL REMOTE NATIONS OF THE WORLD | 105,080 | fin |
| 6 | 12 | Through the Looking-Glass by Lewis Carroll | 29,256 | fin |
| 7 | 35 | The Time Machine by H. G. Wells\** | 32,376 | fin |
| 8 | 16 | Peter Pan by J. M. Barrie | 47,112 | fin |
| 9 | 146 | A Little Princess by Frances Hodgson Burnett | 66,264 | fin |
| 10 | 164 | Twenty Thousand Leagues under the Sea by Jules Verne\** | 104,335 | fin |
| 11 | 521 | ~~The Life and Adventures of Robinson Crusoe by Daniel Defoe~~\*** | 120,792 | fin |
| 12 | 1257 | The three musketeers by Alexandre Dumas and Auguste Maquet | 228,997 | fin |

\*  preprocess_txt.py 実行後人手で I. A Scandal in Bohemia のみを抽出

\** preprocess_txt.py 実行後人手で一部修正

\*** 演習に向いていないため除外 (登場人物が少なすぎる)


### 更新履歴
- 20231125: preprocess_txt.py 完成
- 20231126: summarize.py 完成
- 20231127: create_knowledge_graph.py 完成
- 20231213: 場面分割方法を記載した split_type.txt を追加
    | 分割方法 | id |
    | ---- | ---- |
    | Part \<num\> | 0 |
    | Chapter \<num\> | 1 |
    | \<num\> | 2 |
    | other | 3 |

    * \<num\>: ローマ数字+".", アラビア数字, 数字を表す英単語
    * Part I. の Chapter I. の場合: 01


### コードの説明
- preprocess_txt.py: storyID (gutenbergID) を入力すると, 本文を場面ごとに分割し保存する.
- summarize.py: storyID を入力すると, 各場面の本文の要約を行う.
- create_knowledge_graph: storyID を入力すると, 各場面の node, edge を取得する. (場面の範囲を指定可能)
<!-- - 4_create_json.py: storyID を入力すると, graph.json を作成する. -->
<!-- - create_json.sh: storyID を入力すると, 1~4 をまとめて実行する -->


### 出力例 (3回実行し, 各結果を sample0, 1, 2 に追加)
- 20231127: 18155 ChatGPT-output 追加
- 20231201: 11 ChatGPT-output 追加
- 20231201: 1661 ChatGPT-output 追加
- 20231201: 120 ChatGPT-output 追加 (sample0のみ)
- 20231203: 829 ChatGPT-output 追加 (sample0のみ)
- 20231214: 12 ChatGPT-output 追加 (sample0のみ)
- 20231214: 35 ChatGPT-output 追加 (sample0のみ)
- 20231214: 120 ChatGPT-output 修正
- 20231214: 829 ChatGPT-output 修正
- 20231214: 16 ChatGPT-output 追加 (sample0のみ)
- 20231215: 146 ChatGPT-output 追加 (sample0のみ)
- 20231215: 164 ChatGPT-output 追加 (sample0のみ)
- 20231215: 1257 ChatGPT-output 追加 (sample0のみ)


### コスト概算
- 18155: The Story of the Three Little Pigs (960)
    | program | time | money (I/O, $) |
    | ---- | ---- | ---- |
    | preprocess_txt.py | 0:01 | --- |
    | summarize.py | 0:10 | 0.01/0.01 |
    | create_knowledge_graph.py | 2:30 | 0.03/0.06 |


- 1661: The Adventures of Sherlock Holmes (8,520)
    | program | time | money (I/O, $) |
    | ---- | ---- | ---- |
    | preprocess_txt.py | 0:01 | --- |
    | summarize.py | 0:30 | 0.10/0.01 |
    | create_knowledge_graph.py | 4:00 | 0.25/0.15 |


- 11: Alice's Adventures in Wonderland by Lewis Carroll (26,520)
    | program | time | money (I/O, $) |
    | ---- | ---- | ---- |
    | preprocess_txt.py | 0:01 | --- |
    | summarize.py | 1:00 | 0.30/0.05 |
    | create_knowledge_graph.py | 19:30 | 0.75/0.60 |


- 120: TREASURE ISLAND (67,870)
    | program | time | money (I/O, $) |
    | ---- | ---- | ---- |
    | preprocess_txt.py | 0:01 | --- |
    | summarize.py | 3:30 | 0.70/0.15 |
    | create_knowledge_graph.py | 70:30 | 1.90/1.50 |


- 829: GULLIVER'S TRAVELS INTO SEVERAL REMOTE NATIONS OF THE WORLD (105,080)
    | program | time | money (I/O, $) |
    | ---- | ---- | ---- |
    | preprocess_txt.py | 0:01 | --- |
    | summarize.py | 8:30 | 1.30/0.20 |
    | create_knowledge_graph.py | 48:00 | 2.80/1.60 |


### requirements
- ChatGPT API の利用準備