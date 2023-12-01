## ver2の通信用APIの定義
```
summarized_data := [{obj}, {obj}, ...]

{obj} := {folder} or {file}


{folder} := {
    "sectionName": {sectionName},
    "subSection": [{obj}, {obj}, ...]
}

{file} := {
    "sectionName": {sectionName},
    "summary": {summary},
    "nodes": [{node}, {node}, ...],
    "edges": [{edge}, {edge}, ...]
}

{node} := {
    "id": {node_id},
    "label": {node_label},
    "title": {node_title},
    "group": {group},
    "shape": {shape},
    "image": {image},
    "size": {size}
}

{edge} := {
    "id": {edge_id},
    "label": {edge_label},
    "title": {edge_title},
    "from": {from},
    "to": {to},
    "arrows": {arrow}
}

{sectionName}| String := セクション名
{summary}| String := 各セクションの要約

{node_id}| Number or String := プログラム上での一意なノードの名前（**requied）
{node_label}| String := 画面に表示されるノードの名前
{node_title}| String := マウスをノードに合わせた時に表示される情報
{group}| String := 対象ノードが所属するグループ名
{shape}| String := ノードを画像にしたい場合”image”に設定
{image}| String := 画像のURLを設定（shapeを”image”にすること）
{size}| String := ノードの大きさ（デフォルトで25）
{hidden}| Boolean := エッジを隠すかどうか（デフォルトはfalse、trueで非表示）

{edge_id}| String := エッジのプログラム上での名前
{edge_label}| String := 画面に表示されるエッジの名前
{edge_title}| String := マウスをノードに合わせた時に表示される情報
{from}| Number or String := エッジの始点ノードID（**requied）
{to}| Number or String := エッジの終点ノードID（**requied）
{arrows}| String := エッジの種類（有向エッジのto, from、無向エッジのmiddleがある）
{color}| String := エッジの色（rgb(120,32,14), #ffffff, redのような指定方法がある）
{hidden}| Boolean := エッジを隠すかどうか（デフォルトはfalse、trueで非表示）
```