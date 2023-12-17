# すべての物語の画像生成を行うためのスクリプト
## main_image_gen.pyの引数
# 1: 画像生成の対象となる物語のID
# 2: api_keyのファイルのパス

# 画像生成を行いたいすべての物語のgutenberg IDを指定する
gutenbergIDs=(18155 1661)
api_key_path='./api_key.txt'

for gutenbergID in ${gutenbergIDs[@]}; do
    python main_image_gen.py $gutenbergID $api_key_path
done