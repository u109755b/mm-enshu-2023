## IDのフォルダ内について
```
sample0
のlogについてall_data.jsonを生成

all_data.json：知識グラフ
title.txt：タイトル
```



# ver2の通信用APIの定義
```
summarized_data := [{obj}, {obj}, ...]

{obj} := {folderData} or {fileData}

{folderData} := {
    "sectionName": {sectionName},
    "subSection": [{obj}, {obj}, ...]
}
{fileData} := {
    "sectionName": {sectionName},
    "summary": {summary},
    "nodes": [{node}, {node}, ...],
    "edges": [{edge}, {edge}, ...]
}

{node} := {
    "id": {nodeID},
    "label": {nodeLabel},
    "title": {nodeTitle},
    "group": {group},
    "shape": {shape},
    "image": {image},
    "size": {size}
}
{edge} := {
    "id": {edgeID},
    "label": {edgeLabel},
    "title": {edgeTitle},
    "from": {from},
    "to": {to},
    "arrows": {arrow}
}

{sectionName}| String := セクション名
{summary}| String := 各セクションの要約

{nodeID}| Number or String := プログラム上での一意なノードの名前（**requied）
{nodeLabel}| String := 画面に表示されるノードの名前
{nodeTitle}| String := マウスをノードに合わせた時に表示される情報
{group}| String := 対象ノードが所属するグループ名
{shape}| String := ノードを画像にしたい場合”image”に設定
{image}| String := 画像のURLを設定（shapeを”image”にすること）
{size}| String := ノードの大きさ（デフォルトで25）
{hidden}| Boolean := エッジを隠すかどうか（デフォルトはfalse、trueで非表示）

{edgeID}| String := エッジのプログラム上での名前
{edgeLabel}| String := 画面に表示されるエッジの名前
{edgeTitle}| String := マウスをノードに合わせた時に表示される情報
{from}| Number or String := エッジの始点ノードID（**requied）
{to}| Number or String := エッジの終点ノードID（**requied）
{arrows}| String := エッジの種類（有向エッジのto, from、無向エッジのmiddleがある）
{color}| String := エッジの色（rgb(120,32,14), #ffffff, redのような指定方法がある）
{hidden}| Boolean := エッジを隠すかどうか（デフォルトはfalse、trueで非表示）
```
