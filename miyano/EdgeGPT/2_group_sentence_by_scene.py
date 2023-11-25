from EdgeGPT.EdgeGPT import Chatbot, ConversationStyle
from distutils.util import strtobool
import re
import os
import json
import asyncio
import argparse


# titleを入力すると, 何個の文章に分かれて保存されているか求めて, その数を返す関数
def find_max_sep_idx(title):
    dir_files = os.listdir(f"log/{title}")
    sep_idxs = []
    for file in dir_files:
        try:
            sep_idxs.append(int(re.findall(r"body_(\d+)\.txt", file)[0]))
        except:
            pass
    
    return max(sep_idxs)+1


# ある文章, ある属性について初めてのプロンプトを作成する関数
def make_first_prompt(title, sep_idx, scene_type):
    # 入力文章の読み込み
    with open(f"log/{title}/body_{sep_idx}.txt", encoding="utf-8") as f:
        first_sents = f.read()
    with open(f"log/{title}/body_{sep_idx+1}.txt", encoding="utf-8") as f:
        second_sents = f.read()

    # 各属性のプロンプト
    first_instruct = {
        "location" : (
            "I want to group this sentences based on changes in the location.\n"
            "Please output in the specified format.\n"
            "Example\n'''\n- Location A: sentences 0,1,2\n'''\n"
        ),
        "time" : (
            "I want to group this sentences based on changes in time.\n"
            "Please output in the specified format.\n"
            "Example\n'''\n- The next day: sentences 0,1,2\n'''\n"
        ),
        "character": (
            "I want to group this sentences based on changes in the characters.\n"
            "Please output in the specified format.\n"
            "Example\n'''\n- Character1 and Character2: sentences 0,1,2\n'''\n"
        ),
    }

    return first_instruct[scene_type] + first_sents + second_sents


# int_lineにint-intが含まれる場合, int,int,...,intに修正する関数
def shape_integers(int_line):
    while re.findall(r"\d+-\d+", int_line):
        # int-intの箇所を抜き出す
        line_to_replace = re.findall(r"\d+-\d+", int_line)[0]
        # int,int,...,intに変換
        start_int, end_int = list(map(int, line_to_replace.split("-")))
        replaced_line = ",".join(map(str, range(start_int, end_int+1)))
        # int_lineの更新
        int_line = int_line.replace(line_to_replace, replaced_line)
    
    return int_line


# response, one_attribute_information_dictを入力すると, responseを基にone_attribute_information_dictを更新する関数
def update_one_attribute_information_dict(response, one_attribute_information_dict):
    for response_line in response["text"].split("\n"):
        try:
            # 場面名, 対応する文idxを抽出
            # 文idx-文idxを, 文idx,文idx,文idxに変換する
            response_line = shape_integers(response_line)
            # 対応形式: "- 場面名: sentences 文idx,文idx,文idx" or "- 場面名: sentences 文idx, 文idx, 文idx"
            response_scene, response_sentences = re.findall(r"- (.+): sentence[s?] ([\s?\d+,]*\s?\d+)", response_line)[0]
            response_sentence_list = list(map(int, response_sentences.split(",")))
            for response_sentence in response_sentence_list:
                # one_attribute_information_dictの更新
                one_attribute_information_dict[response_sentence].add(response_scene)
        except:
            # 出力形式に対応していない場合はパス
            pass
    
    return one_attribute_information_dict


# titleとretry_sentence_idxを入力すると, retry_sentence_idxに対応する文の周囲の文章を抜き出す関数
def get_context_around_sentences(title, retry_sentence_idx):
    # 文単位に分割された本文を読み込む
    with open(f"log/{title}/body.txt", encoding="utf-8") as f:
        sentences = f.read().split("\n")[:-1]
    
    # retry_sentence_idxに対応する文の前/後1800文字分の文章を格納する
    context_sentences_before, context_sentences_after = [], []
    total_len_before, total_len_after = 0, 0
    for sentence_idx in range(retry_sentence_idx-1, -1, -1):
        sentence = sentences[sentence_idx]
        # 改行も1文字とカウントされるため, 文の長さに1を追加
        sentence_len = len(sentence) + 1
        # context_sentences_beforeの長さが1800文字未満の場合: そのまま追加
        if total_len_before + sentence_len < 1800:
            context_sentences_before.append(sentence)
            total_len_before += sentence_len
        # context_sentences_beforeの長さが1800文字以上の場合: 終了
        else:
            break
    for sentence_idx in range(retry_sentence_idx+1, len(sentences)):
        sentence = sentences[sentence_idx]
        # 改行も1文字とカウントされるため, 文の長さに1を追加
        sentence_len = len(sentence) + 1
        # context_sentences_afterの長さが1800文字未満の場合: そのまま追加
        if total_len_after + sentence_len < 1800:
            context_sentences_after.append(sentence)
            total_len_after += sentence_len
        # context_sentences_afterの長さが1800文字以上の場合: 終了
        else:
            break
    
    context_sentences_before = context_sentences_before[::-1]
    context_before = "\n".join(context_sentences_before) + "\n"
    context_after = "\n".join(context_sentences_after) + "\n"
    center_sentence = sentences[retry_sentence_idx] + "\n"

    return context_before, center_sentence, context_after


# ある文のある属性について, 候補のうちどれに属するか確認するプロンプトを作成する関数
def make_retry_prompt(title, scene_type, retry_sent_idx, candidates):
    # 入力文章の読み込み
    retry_context_before, retry_center_sentence, retry_context_after = get_context_around_sentences(title, retry_sent_idx)

    # 各属性のプロンプト
    retry_instruct = {
        "location" : "I want to group this sentences based on changes in the location.\n",
        "time"     : "I want to group this sentences based on changes in time.\n",
        "character": "I want to group this sentences based on changes in the characters.\n",
    }

    # この文をどの属性についても追加で聞く
    # 候補数を増やせるように拡張
    select_candidates = " or ".join([f"'{candidate}'" for candidate in candidates])
    select_instruct = (
        f"Does The sentence {retry_sent_idx} belong to {select_candidates}?\n"
        f"Please answer only {select_candidates}.\n"
    )

    return retry_instruct[scene_type] + select_instruct + retry_context_before + retry_center_sentence + retry_context_after



async def main():
    # 設定
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", type=str, default="The Story of the Three Little Pigs")
    parser.add_argument("--scene_type", type=str, default="location", choices=["location", "time", "character"])
    parser.add_argument("--show_log", type=str, default="False")
    args = parser.parse_args()

    title = args.title
    scene_type = args.scene_type
    show_log = strtobool(args.show_log)

    # すでに分類済みの場合, 実行しない
    if os.path.exists(f"log/{title}/body_info_{scene_type}.txt"):
        print("Grouping result has already existed!")
        exit()
    
    # 前処理済みの本文が存在しない場合, 先に1_preprocess_txt.pyを実行するように促す
    if not os.path.exists(f"log/{title}/body.txt"):
        print("The preprocessed text doesn't exist!")
        print(f"Please run 'python 1_preprocess_txt.py --title {title}'")

    # EdgeGPTの設定
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cookie_path = os.path.join(script_dir, 'bing_cookies_.json')
    cookies = json.loads(open(cookie_path, encoding="utf-8").read())
    bot = await Chatbot.create(cookies=cookies)

    # 入力の読み込み
    max_sep_idx = find_max_sep_idx(title)
    with open(f"log/{title}/body.txt", encoding="utf-8") as f:
        sentences = f.read().split("\n")[:-1]


    # 一つの属性について, 各文の分類結果を保存するdict
    one_attribute_information_dict = {sentence_idx:set() for sentence_idx in range(len(sentences))}
    # ある文章, ある属性について初めてのプロンプトを入力し, dictを更新
    for sep_idx in range(max_sep_idx-1):
        prompt = make_first_prompt(title, sep_idx, scene_type)
        print(f"Asking for the following prompts...\n{prompt}\n") if show_log else None
        response = await bot.ask(prompt=prompt, conversation_style=ConversationStyle.creative, simplify_response=True)
        print(f"Get the following response!\n{response['text']}\n") if show_log else None

        one_attribute_information_dict = update_one_attribute_information_dict(response, one_attribute_information_dict)


    # 各文について, 分類結果を確定させていく
    # 各文の分類結果を格納
    one_attribute_groups = [""] * len(sentences)
    is_finiseds = [0] * len(sentences)

    # 全ての分類候補を用意
    all_candidates = set()
    for sentence_idx in range(len(sentences)):
        all_candidates |= one_attribute_information_dict[sentence_idx]

    # 1. 分類結果が1通りの場合, 分類結果を確定させる
    for sentence_idx in range(len(sentences)):
        if len(one_attribute_information_dict[sentence_idx]) == 1:
            one_attribute_groups[sentence_idx] = one_attribute_information_dict[sentence_idx].pop()
            is_finiseds[sentence_idx] = 1

    # 2. 分類結果が2通り以上の場合, EdgeGPTにどの分類結果が正しいか確認する
    for sentence_idx in range(len(sentences)):
        # 分類済みの場合continue
        if is_finiseds[sentence_idx]:
            continue
        # 分類結果が2通り以上の場合, どの分類結果が正しいか確認し, 出力された結果を最終的な分類結果とする
        if len(one_attribute_information_dict[sentence_idx]) > 1:
            # 分類候補を基にプロンプトを作成し, 結果を得る
            retry_candidates = one_attribute_information_dict[sentence_idx]
            prompt = make_retry_prompt(title, scene_type, sentence_idx, retry_candidates)
            print(f"Asking for the following prompts...\n{prompt}\n") if show_log else None
            response = await bot.ask(prompt=prompt, conversation_style=ConversationStyle.creative, simplify_response=True)
            print(f"Get the following response!\n{response['text']}\n") if show_log else None

            # 全ての分類候補の内, responseに含まれるものを最終的な分類結果とする
            # 複数含まれる場合, 最初に含まれるものを最終的な分類結果とする
            for retry_candidate in all_candidates:
                if retry_candidate in response['text']:
                    one_attribute_groups[sentence_idx] = retry_candidate
                    is_finiseds[sentence_idx] = 1
                    one_attribute_information_dict[sentence_idx] = set()
                    break
    
    # 3. 分類結果が存在しない場合, 前後の分類済み文の2つの分類結果から, EdgeGPTを用いて分類を選択
    for sentence_idx in range(len(sentences)):
        # 分類済みの場合continue
        if is_finiseds[sentence_idx]:
            continue
        # 分類結果が存在しない場合, 前後の分類済み文の2つの分類結果から分類を選択
        # 分類候補の決定
        retry_candidates = set()
        # 前方の分類済みの文の分類結果を追加
        for before_sentence_idx in range(sentence_idx-1, -1, -1):
            if is_finiseds[before_sentence_idx]:
                retry_candidates.add(one_attribute_groups[before_sentence_idx])
                break
        # 後方の分類済みの文の分類結果を追加
        for after_sentence_idx in range(sentence_idx+1, len(sentences)):
            if is_finiseds[after_sentence_idx]:
                retry_candidates.add(one_attribute_groups[after_sentence_idx])
                break
        
        # 分類候補が1つしかない場合, その分類を最終的な分類結果とする
        if len(retry_candidates) == 1:
            one_attribute_groups[sentence_idx] = retry_candidates.pop()
            is_finiseds[sentence_idx] = 1
        # 分類候補が2つある場合, その中から分類結果を決定
        elif len(retry_candidates) == 2:
            # 分類候補を基にプロンプトを作成し, 結果を得る
            prompt = make_retry_prompt(title, scene_type, sentence_idx, retry_candidates)
            print(f"Asking for the following prompts...\n{prompt}\n") if show_log else None
            response = await bot.ask(prompt=prompt, conversation_style=ConversationStyle.creative, simplify_response=True)
            print(f"Get the following response!\n{response['text']}\n") if show_log else None

            # 全ての分類候補の内, responseに含まれるものを最終的な分類結果とする
            # 複数含まれる場合, 最初に含まれるものを最終的な分類結果とする
            for retry_candidate in all_candidates:
                if retry_candidate in response['text']:
                    one_attribute_groups[sentence_idx] = retry_candidate
                    is_finiseds[sentence_idx] = 1
                    one_attribute_information_dict[sentence_idx] = set()
                    break
            
            # 決定できない場合, 前方の分類結果を最終的な分類結果とする
            if is_finiseds[sentence_idx] == 0:
                one_attribute_groups[sentence_idx] = retry_candidates.pop()
                is_finiseds[sentence_idx] = 1
    

    # 分類結果を保存
    with open(f"log/{title}/body_info_{scene_type}.txt", "w", encoding="utf-8") as f:
        for sentence_idx, sentence_group in enumerate(one_attribute_groups):
            f.write(f"{sentence_idx}\t{sentence_group}\n")
    
    await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
