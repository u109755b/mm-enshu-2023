#!/usr/bin/env python
# coding: utf-8

# 物語IDを選択
# 
# ### 対象物語 (随時追加予定)
# | num | gutenbergID | name | #words | condition |
# | ---- | ---- | ---- | ---- | ---- |
# | 1 | 18155 | The Story of the Three Little Pigs | 960 | fin |
# | 2 | 1661 | The Adventures of Sherlock Holmes\* | 8,520 | fin |
# | 3 | 11 |  Alice's Adventures in Wonderland by Lewis Carroll | 26,520 | fin |
# | 4 | 120 | TREASURE ISLAND | 67,870 | fin |
# | 5 | 829 | GULLIVER'S TRAVELS INTO SEVERAL REMOTE NATIONS OF THE WORLD | 105,080 | fin |
# | 6 | 12 | Through the Looking-Glass by Lewis Carroll | 29,256 | fin |
# | 7 | 35 | The Time Machine by H. G. Wells\** | 32,376 | fin |
# | 8 | 16 | Peter Pan by J. M. Barrie | 47,112 | fin |
# | 9 | 146 | A Little Princess by Frances Hodgson Burnett | 66,264 | fin |
# | 10 | 164 | Twenty Thousand Leagues under the Sea by Jules Verne\** | 104,335 | fin |
# | 11 | 521 | ~~The Life and Adventures of Robinson Crusoe by Daniel Defoe~~\*** | 120,792 | fin |
# | 12 | 1257 | The three musketeers by Alexandre Dumas and Auguste Maquet | 228,997 | fin |
# 
# 

# In[1]:


#インポート
import sys
import glob
from tqdm import tqdm
import itertools
import os
import json
import difflib
import Levenshtein
import textwrap
from difflib import SequenceMatcher


# In[2]:


os.chdir('log')


# In[3]:


#IDと物語名の辞書を構築しておく
story_d={
    "The Story of the Three Little Pigs":'18155',
    "The Adventures of Sherlock Holmes":'1661',
    "Alice's Adventures in Wonderland":'11',
    "Treasure Island":'120',
    "Gulliver's Travels":'829',
    "Through the Looking-Glass":"12",
    "The Time Machine":"35",
    "Peter Pan":"16",
    "A Little Princess":"146",
    "Twenty Thousand Leagues under the Sea":"164",
    "The Three Musketeers":"1257",
}


# In[4]:


#物語タイトル
title_name="A Little Princess"


# In[5]:


ID=story_d[title_name]


# テキストファイルから情報を抽出  
# 全ての物語でこのプログラムを動かしたら抽出できるようにする

# In[6]:


#可変の変数
size_magnification = 30 #サイズの倍率(変数)10 重要度とかける
image_min_size=15 #画像の最小サイズ
max_edge_label_len=40 #edgeのlabelの文字数を最大何文字にするか

#sample0について実行
sample_file='sample0'


# In[7]:


#事前に変数定義
node_list=[]
edge_list=[]
summary_list=[]
chapter_name_list=[]
section_name_list=[]
summarized_data=[]

section_json_flag=-1


#分割数をカウント（divide_count）
divide_count=len(glob.glob(f'./{ID}/body_scene*.txt', recursive=False))
print(divide_count)


# In[8]:


#chapter_listの作成（章と節がともに存在する場合のみ）
#章が何番で区切られているか確認してリストを作成(話によって異なる)
if ID=='120':
  chapter_list=[0,6,12,15,21,27]
  section_json_flag=1

elif ID=='1661':
  chapter_list=[0]
  section_json_flag=1

elif ID=='829':
  #partが一番大きなくくり，次点がchapterなので，part→chapter,chapter→sectionに対応させる
  chapter_list=[0,1,2,10,18,29]
  section_json_flag=1

elif ID=='164':
  #partが一番大きなくくり，次点がchapterなので，part→chapter,chapter→sectionに対応させる
  chapter_list=[0,23]
  section_json_flag=1

else:
   chapter_list=[0]


# # 処理を関数化する

# ## 章，節名の抽出

# ### sectionがある場合

# In[9]:


#物語ことに処理を追加（手動）

def create_section(ID,divide_count,chapter_list,chapter_name_list,section_name_list):
  chapter_num=0 #章番号
  section_num=0 #節番号

  for i in range(divide_count):
    chapter_file = open(f'{ID}/body_scene{i}.txt', 'r', encoding="utf-8")
    lines = chapter_file.readlines()

    #section_nameの決定(IDごとに異なる)
    if ID=='120':
      #章になっているとき
      if i in chapter_list:
        chapter_name=lines[0].strip() #ファイルの最初の行をchapter_titleとする
        chapter_name_list.append(chapter_name)

        #章を更新すると，節の番号はリセット
        chapter_num+=1
        section_num=1

        #章があるときは三行目に節タイトル
        section_name=f'chapter{chapter_num}_{section_num} {i+1} {lines[2].strip()}'

      else:
        #章タイトルがないとき
        #節のタイトルは2行目
        section_num+=1
        section_name=f'chapter{chapter_num}_{section_num} {i+1} {lines[1].strip()}'

    elif ID=='1661':
      #章になっているとき
      if i in chapter_list:
        chapter_name=lines[0].strip() #ファイルの最初の行をchapter_titleとする
        chapter_name_list.append(chapter_name)
        #章を更新すると，節の番号はリセット
        chapter_num+=1
        section_num=1
      #節のタイトルは適当に付ける
      section_name=f'section{chapter_num}_{section_num}'
      section_num+=1

    elif ID=='829':
      if i in chapter_list:
        chapter_name=lines[0].strip() #ファイルの最初の行をchapter_titleとする
        chapter_name_list.append(chapter_name)
        #章を更新すると，節の番号はリセット
        chapter_num+=1
        section_num=1
        #0番目と1番目が少し特殊なので場合分け
        if i==0 or i==1:
          section_name=f'chapter{chapter_num}_{section_num}'
        else:
          #章があるときは2行目に節タイトル
          section_name=f'chapter{chapter_num}_{section_num} {lines[1].strip()}'
      else:
        # 章タイトルがないとき
        #節のタイトルは1行目
        section_name=f'chapter{chapter_num}_{section_num} {lines[0].strip()}'
        section_num+=1
        
    
    elif ID=='164':
      if i in chapter_list:
        chapter_name=lines[0].strip() #ファイルの最初の行をchapter_titleとする
        chapter_name_list.append(chapter_name)
        #章があるときは2行目に節タイトル
        section_name=lines[1].strip()
      else:
        #章がないときは1行目に節タイトル
        section_name=lines[0].strip()

    #節名を追加
    section_name_list.append(section_name)


# ### sectionがない場合

# In[10]:


def create_non_section(ID,divide_count,chapter_name_list):
  if ID=='18155':
    chapter_name_list.append('Chapter1')
  elif (ID=='35') or (ID=='146'):
    for i in range(divide_count):
      #chapter_nameの決定
      chapter_file = open(f'{ID}/body_scene{i}.txt', 'r', encoding="utf-8")
      lines = chapter_file.readlines()
      chapter_name=f"{lines[0].strip()} {lines[1].strip()}"#ファイルの最初の行と2行目を合わせたものをchapter_titleとする
      chapter_name_list.append(chapter_name)
  else: #11,12,16,1257
    for i in range(divide_count):
      #chapter_nameの決定
      chapter_file = open(f'{ID}/body_scene{i}.txt', 'r', encoding="utf-8")
      lines = chapter_file.readlines()
      chapter_name=lines[0].strip() #ファイルの最初の行をchapter_titleとする
      chapter_name_list.append(chapter_name)


# ## nodeとedgeの処理

# In[11]:


def create_node_edge(ID,divide_count,node_list,edge_list,sample_file='sample0',size_magnification =10,image_min_size=20):
  node_id_num=0
  edge_id_num=0

  for i in range(divide_count):
    node_list_i=[]
    edge_list_i=[]

    #nodeについての処理
    node_file = open(f'./{ID}/{sample_file}/node_scene{i}.txt', 'r', encoding="utf-8")
    lines = node_file.readlines()    
    
    for j in range(len(lines)):
      line=lines[j]
      #左から分割
      lists = line.split(',',1)

      #右から分割
      r_lists=lists[1].rsplit(',',1)

      #抽出
      label = lists[0].strip()
      title=r_lists[0].strip()


      #重要度がしっかりしていない箇所がある（その場合重要度0）
      try:
        important_rate=float(r_lists[1].strip())

      except ValueError:
        important_rate=0

      #サイズはimportant_rateを基に決定
      size=int(image_min_size+important_rate*size_magnification)

      #辞書化する(idは適当に番号文字列)
      node_d={
          "id":f'node_id{node_id_num}',
          "label":label,
          "title":title,
          "size":size,
        }

      node_list_i.append(node_d)

      node_id_num+=1


    #nodeの統合処理をするならここで処理

    #全体のリストに追加
    node_list.append(node_list_i)


    #edgeについての処理
    edge_file = open(f'./{ID}/{sample_file}/edge_scene{i}.txt', 'r', encoding="utf-8")
    lines = edge_file.readlines()
        

    for j in range(len(lines)):
      line=lines[j]
      #左から分割
      lists = line.split(',',1)

      lists2=lists[1].split(',',1)

      lists3=lists2[1].split(',',1)


      #抽出
      edge_from = lists[0].strip()
      edge_to = lists2[0].strip()
      edge_label=lists3[0].strip()
      edge_title=lists3[1].strip()
      
      #以下edge_labelの例外処理
      #edge_labelに / が含まれる場合その前だけ出力
      if '/' in edge_label:
        edge_label=edge_label.split('/')[0]
      #edge_labelに & が含まれる場合その前だけ出力
      if '&' in edge_label:
        edge_label=edge_label.split('&')[0]
      #edge_labelが長すぎる場合に省略(字数制限)
      edge_label=textwrap.shorten(edge_label, max_edge_label_len, placeholder='~')


      #from と to　を示すものが nodeにあるか確認
      #あった場合そのidを抽出し，edge_from_idとedge_to_idに与える
      from_flag=0
      to_flag=0

      for k in range(len(node_list_i)):
        #node_list_i[k]は辞書を表す
        if (from_flag==0) and (node_list_i[k]['label']==edge_from):
          edge_from_id= node_list_i[k]['id']
          from_flag=1


        if (to_flag==0) and (node_list_i[k]['label']==edge_to):
          edge_to_id= node_list_i[k]['id']
          to_flag=1
        
        if from_flag ==1 and to_flag==1:
            break

      #どちらかなかったら近いnodeを類似度により探す
      if (from_flag==0):
        max_similarity = 0
        for k in range(len(node_list_i)):  
            dist = SequenceMatcher(None,edge_from,node_list_i[k]['label']).ratio()
            if max_similarity < dist:
                max_similarity=dist
                edge_from_id = node_list_i[k]['id']
        
      if (to_flag==0):
         max_similarity = 0
         for k in range(len(node_list_i)):  
             dist = SequenceMatcher(None,edge_from,node_list_i[k]['label']).ratio()
             if max_similarity <= dist:
                 max_similarity=dist
                 edge_to_id = node_list_i[k]['id']
        
            
        
        
      #過去に出てきた例とedge_from_idとedge_to_idが完全一致してしまった場合
      #edge_labelは最初の1つだけ使用，edge_titleは<br>でくっつける
      match_flag=0
      for k in range(len(edge_list_i)):
        #edge_list_i[k]は辞書を表す
        if (edge_list_i[k]['from']==edge_from_id) and (edge_list_i[k]['to']==edge_to_id):
            edge_list_i[k]['title']= f"{edge_list_i[k]['title']}<br>{edge_title}"
            match_flag=1
            break

      #過去に出てきた例とedge_from_idとedge_to_idが完全一致しなかった場合
      if match_flag==0:
        #辞書化する(idは一意の番号文字列,矢印を追加(allows))
          edge_d={
              "id":f'edge_id{edge_id_num}',
              "label":edge_label,
              "title":edge_title,
              "from":edge_from_id,
              "to":edge_to_id,
              "arrows": "to",
            }

          #辞書を追加
          edge_list_i.append(edge_d)

          #edgeのnumを増やす
          edge_id_num+=1


    #edgeの統合処理をするならここで処理
    #edge_list_i内でfrom to と to fromが同じものが存在する場合，矢印をカーブさせる
    for pair in itertools.combinations(edge_list_i, 2):
      if (pair[0]['from']==pair[1]['to']) and (pair[1]['from']==pair[0]['to']):
        f_t=pair[0]['id']
        t_f=pair[1]['id']
        for j in range(len(edge_list_i)):
          if edge_list_i[j]['id']== f_t or t_f:
            edge_list_i[j]['smooth']= {
                                      "type": "curvedCW",
                                      "roundness": 0.3
                                  }

    #全体のリストに追加
    edge_list.append(edge_list_i)


# ## summaryの処理

# In[12]:


def create_summary(ID,divide_count,summary_list,sample_file='sample0'):
 for i in range(divide_count):
   summary_file = open(f'{ID}/{sample_file}/summary.txt', 'r', encoding="utf-8")
   lines = summary_file.readlines()
   summary=lines[i].strip()
   summary_list.append(summary)


# ## 外部ファイルに出力
# 

# ### sectionがある場合

# In[13]:


def section_json(chapter_list,summarized_data):
  for i in range(len(chapter_list)):
    chapter_summarized_data=[]

    #chapterがあるbody_sceneについてその間の節を抜き出していく
    if i!=len(chapter_list)-1:
      for j in range(chapter_list[i],chapter_list[i+1]):

        summarized_file={
            "sectionName":section_name_list[j],
            "summary":summary_list[j],
            "nodes":node_list[j],
            "edges":edge_list[j],
        }

        chapter_summarized_data.append(summarized_file)
    #chapterがあるbody_sceneについて，最後のchapterからは最後まで
    else:
      for j in range(chapter_list[i],divide_count):

        summarized_file={
            "sectionName":section_name_list[j],
            "summary":summary_list[j],
            "nodes":node_list[j],
            "edges":edge_list[j],
        }

        chapter_summarized_data.append(summarized_file)


    summarized_folder={
        "sectionName":chapter_name_list[i],
        "subSection":chapter_summarized_data,
    }

    summarized_data.append(summarized_folder)


# ### sectionがない場合

# In[14]:


def non_section_json(divide_count,summarized_data):
  for i in range(divide_count):
    summarized_file={
        "sectionName":chapter_name_list[i],
        "summary":summary_list[i],
        "nodes":node_list[i],
        "edges":edge_list[i],
    }

    summarized_data.append(summarized_file)


# # 全体的な処理

# In[15]:


print(f'ID : {ID} title : {title_name}')

if section_json_flag==1:
  create_section(ID,divide_count,chapter_list,chapter_name_list,section_name_list)
else:
  create_non_section(ID,divide_count,chapter_name_list)

create_node_edge(ID,divide_count,node_list,edge_list,sample_file,size_magnification,image_min_size)

create_summary(ID,divide_count,summary_list,sample_file)

if section_json_flag==1:
  section_json(chapter_list,summarized_data)
else:
  non_section_json(divide_count,summarized_data)


# ## 保存

# In[16]:


new_dir_path_recursive=f'../summarized_data/{ID}/{sample_file}'
os.makedirs(new_dir_path_recursive, exist_ok=True)
os.chdir(new_dir_path_recursive)


# In[17]:


with open("all_data.json", "w", encoding="utf-8") as f:
    json.dump(summarized_data,f,indent=4)
f.close()


# In[18]:


#タイトルを含んだtxtの生成
with open("../title.txt", "w", encoding="utf-8") as f:
    f.write(title_name)
f.close()


# # 出力の確認

# In[19]:


print(f'node_list\n{node_list}')
print(f'\nedge_list\n{edge_list}')
print(f'\nsummary_list\n{summary_list}')
print(f'\nchapter_name_list\n{chapter_name_list}')
print(f'\nsection_name_list\n{section_name_list}')
print(f'\nsummarized_data\n{summarized_data}')


# In[ ]:




