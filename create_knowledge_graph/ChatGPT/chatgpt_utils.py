import os
import re

# API key, model を指定
# API key は各自で指定
GPT_KEY = "YOUR API KEY"
GPT_MODEL = "gpt-4-1106-preview"

# storyID を入力すると, 何個の文章に分かれて保存されているか求めてその数を返す関数
def get_scene_num(storyID):
    dir_files = os.listdir(f"log/{storyID}")
    sceneIDs = []
    file_pattern = re.compile(f"body_scene(\d+)\.txt")
    for file in dir_files:
        try:
            sceneIDs.append(int(re.findall(file_pattern, file)[0]))
        except:
            pass
    
    return max(sceneIDs)+1

