from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch
import json
import os
import argparse


# テキストを入力すると, 入力長の5~20%に要約する
# 性能が良くないため, 他の方法を用いる予定
# 使用方法 python summarization_hf.py --text_path "要約したいテキストのパス" --json_path "要約を保存するjsonのパス"
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--text_path', type=str)
    parser.add_argument('--json_path', type=str)
    args = parser.parse_args()

    text_path = args.text_path
    json_path = args.json_path


    checkpoint = "pszemraj/bigbird-pegasus-large-K-booksum"
    device = torch.device('cuda:0') if torch.cuda.is_available() else torch.device('cpu')

    # モデルの定義
    model = AutoModelForSeq2SeqLM.from_pretrained(checkpoint).to(device)
    tokenizer = AutoTokenizer.from_pretrained(checkpoint)

    # 入力の前処理
    with open(text_path, "r", encoding="utf-8") as f:
        input_text = f.read()[:-1]

    input_ids = tokenizer(input_text, return_tensors="pt").to(device)
    input_len = len(input_ids["input_ids"][0])

    # 要約の実行
    output_ids = model.generate(
        **input_ids,
        num_beams=5,
        no_repeat_ngram_size=3,
        min_length=int(0.05*input_len),     # 要約長は入力長の5%以上
        max_length=int(0.2*input_len),      # 要約長は入力長の20%以下
    )

    # 出力の後処理
    output_text = tokenizer.batch_decode(output_ids, skip_special_tokens=True)[0]


    # jsonファイルの準備
    if os.path.exists(json_path):
        # jsonが存在する場合, 読み込む
        with open(json_path, "r", encoding="utf-8") as f:
            json_dict = json.load(f)
    else:
        # 存在しない場合, 空のdictを新たに作成
        json_dict = {"title":"", "summary":"", "nodes":[], "edges":[]}

    # 要約を上書き
    json_dict["summary"] = [output_text]

    # jsonファイルへの書き込み
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_dict, f)


if __name__ == "__main__":
    main()
