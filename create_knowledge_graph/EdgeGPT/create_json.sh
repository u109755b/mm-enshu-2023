# 1~6を一括で実行

TITLE=$1
USE_LOCATION=$2     # 場面分割の基準に場所の変化を使うかどうかを指定 (true or false)
USE_TIME=$3         # 場面分割の基準に時間の変化を使うかどうかを指定 (true or false)
USE_CHARACTER=$4    # 場面分割の基準に登場人物の変化を使うかどうかを指定 (true or false)
SHOW_LOG=$5         # EdgeGPTとの応答のlogを表示するかどうかを指定 (true or false)

python 1_preprocess_txt.py --title "${TITLE}" ;

if "${USE_LOCATION}"; then
    python 2_group_sentence_by_scene.py --title "${TITLE}" --scene_type "location" --show_log ${SHOW_LOG} ;
fi

if "${USE_TIME}"; then
    python 2_group_sentence_by_scene.py --title "${TITLE}" --scene_type "time" --show_log ${SHOW_LOG} ;
fi

if "${USE_CHARACTER}"; then
    python 2_group_sentence_by_scene.py --title "${TITLE}" --scene_type "character" --show_log ${SHOW_LOG} ;
fi

python 3_split_body_by_scene.py --title "${TITLE}" --use_location ${USE_LOCATION} --use_time ${USE_TIME} --use_character ${USE_CHARACTER} ;

python 4_summarize_splited_body.py --title "${TITLE}" --use_location ${USE_LOCATION} --use_time ${USE_TIME} --use_character ${USE_CHARACTER} --show_log ${SHOW_LOG} ;

python 5_create_knowledge_graph.py --title "${TITLE}" --use_location ${USE_LOCATION} --use_time ${USE_TIME} --use_character ${USE_CHARACTER} --show_log ${SHOW_LOG} ;

python 6_create_json.py --title "${TITLE}" --use_location ${USE_LOCATION} --use_time ${USE_TIME} --use_character ${USE_CHARACTER}
