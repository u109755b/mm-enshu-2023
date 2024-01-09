import os
import argparse
from utils.novel_format_utils import get_cache_file_from_gutenberg
from utils.constants import MODEL2PATH, MODEL2TEPLATE, TASK2PROMPT
from utils.milvus_utils import (
    create_novel_collection,
    add_chunks_to_collection,
    search_top_chunks,
)
from utils.novel_format_utils import save_cache_file
from utils.copilot_utils import get_current_progress
from vllm import LLM, SamplingParams
from pymilvus import connections, Collection
from sentence_transformers import SentenceTransformer
from flashrank import Ranker, RerankRequest

# This program is a prototype of the reading assistant system.

parser = argparse.ArgumentParser()
parser.add_argument(
    "--GutenbergID",
    "-id",
    type=int,
    help="The gutenberg id to identify the book.",
    required=True,
)
parser.add_argument("--top_p", "-topp", type=float, help="Top-P", default=0.9)
parser.add_argument(
    "--temperature", "-temp", type=float, help="Temperature", default=0.35
)
parser.add_argument(
    "--model", type=str, help="Name or path to the model.", default="openhermes"
)
parser.add_argument("--max_new_token", type=int, default=4096)
args = parser.parse_args()


def chat(template, user_message, model, sampling_params) -> str:
    prompt = template.format(user_message=user_message)
    outputs = model.generate(prompt, sampling_params)
    generated_text = outputs[0].outputs[0].text
    return prompt, generated_text.strip()


def main():
    # If the novel is not cached, download it from Gutenberg.
    save_dir = os.path.join(os.getcwd(), "cache/Gutenberg", str(args.GutenbergID))
    info, body_chapters, body_pages = get_cache_file_from_gutenberg(
        save_dir, args.GutenbergID
    )
    print(body_pages[0])
    for item in ["Title", "Author"]:
        print(f"{item}: {info[item]}")

    # If there is no collection in Milvus database, create one and add chunks to it.
    embedding_model = SentenceTransformer("BAAI/bge-base-en-v1.5")
    ranker = Ranker(model_name="rank-T5-flan", cache_dir="/workspace/models")
    if create_novel_collection(args.GutenbergID, dim=768):
        print("Embedding novel pages by chunks...")
        embedding_list = []
        page_list = []
        sentence_list = []
        for i, page in enumerate(body_pages):
            i
            for j, sentence in enumerate(page):
                if len(sentence.split()) < 10:
                    continue
                sentence_embedding = embedding_model.encode(
                    sentence, normalize_embeddings=True
                )
                page_list.append(i)
                sentence_list.append(j)
                embedding_list.append(sentence_embedding)
            print(f"\rPage {i+1} embedded.", end="")
        add_chunks_to_collection(
            args.GutenbergID, embedding_list, page_list, sentence_list
        )

    # Load LLM for question answering.
    model = LLM(model=MODEL2PATH[args.model])
    sampling_params = SamplingParams(
        temperature=args.temperature, top_p=args.top_p, max_tokens=args.max_new_token
    )
    template = MODEL2TEPLATE[args.model]

    log = []
    page_num_total = len(body_pages)
    current_progress = get_current_progress(1, page_num_total)
    connections.connect(alias="default", host="chou_milvus-standalone", port="19530")
    collection = Collection(name=f"novel_{args.GutenbergID}")
    collection.load()

    # After comformation, start the chatbot.
    while True:
        user_input = input(
            "Enter the question you'd like to ask (type 'END' to exit): "
        )

        if user_input.strip().upper() == "END":
            print("Exiting the program.")
            break

        user_input_vector = embedding_model.encode(
            "Represent this sentence for searching relevant passages: " + user_input,
            normalize_embeddings=True,
        )
        top_results = search_top_chunks(collection, user_input_vector, current_progress)
        top_text = [
            body_pages[result["page_id"]][result["sentence_id"]]
            for result in top_results
        ]
        passages = [{"text": text} for text in top_text]
        print(passages[0], len(passages))
        ranker.rerank(RerankRequest(query=user_input, passages=passages))
        print(passages[0])
        user_message = TASK2PROMPT["copliot_answering"].format(
            contents="\n".join([d["text"] for d in passages][:5]), question=user_input
        )
        prompt, response = chat(template, user_message, model, sampling_params)
        print("\n" + "-" * 50 + "\n")
        print(response)
        print("\n" + "-" * 50 + "\n")
        log.append({"prompt": prompt, "response": response})

    save_cache_file(save_dir, log, "log.json")
    collection.release()
    connections.disconnect(alias="default")


if __name__ == "__main__":
    main()
